#!/usr/bin/env python3

import argparse
from datetime import date
import math
import multiprocessing as mp
import os
import subprocess
import sys

from wpiformat.clangformat import ClangFormat
from wpiformat.config import Config
from wpiformat.includeorder import IncludeOrder
from wpiformat.licenseupdate import LicenseUpdate
from wpiformat.lint import Lint
from wpiformat.namespace import Namespace
from wpiformat.newline import Newline
from wpiformat.pyformat import PyFormat
from wpiformat.stdlib import Stdlib
from wpiformat import task
from wpiformat.whitespace import Whitespace


def in_git_repo(directory):
    """Check that the current directory is part of a Git repository.
    """
    cmd = ["git", "rev-parse"]
    returncode = subprocess.call(cmd, stderr=subprocess.DEVNULL)
    return returncode == 0


def get_repo_root():
    """Get the Git repository root as an absolute path.
    """
    current_dir = os.path.abspath(os.getcwd())
    while current_dir != os.path.dirname(current_dir):
        if os.path.exists(current_dir + os.sep + ".git"):
            return current_dir
        current_dir = os.path.dirname(current_dir)


def filter_ignored_files(names):
    """Returns list of files not in .gitignore.
    """
    cmd = ["git", "check-ignore", "--no-index", "-n", "-v", "--stdin"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    # "git check-ignore" misbehaves when the names are separated by "\r\n" on
    # Windows, so os.linesep isn't used here.
    output = proc.communicate("\n".join(names).encode())[0]

    # "git check-ignore" prefixes the names of non-ignored files with "::",
    # wraps names in quotes on Windows, and outputs "\n" line separators on all
    # platforms.
    return [
        name[2:].lstrip().strip("\"").replace("\\\\", "\\")
        for name in output.decode().split("\n") if name[0:2] == "::"
    ]


def proc_init(task_pipeline_copy, verbose1_copy, verbose2_copy):
    global task_pipeline
    global verbose1
    global verbose2
    global print_lock

    task_pipeline = task_pipeline_copy
    verbose1 = verbose1_copy
    verbose2 = verbose2_copy
    print_lock = mp.Lock()


def proc_pipeline(name):
    """Runs the contents of each files through the task pipeline.

    If the contents were modified at any point, the result is written back out
    to the file.
    """
    config_file = Config(os.path.dirname(name), ".styleguide")
    if verbose1 or verbose2:
        with print_lock:
            print("Processing", name)
            if verbose2:
                for subtask in task_pipeline:
                    if subtask.should_process_file(config_file, name):
                        print("  with " + type(subtask).__name__)

    lines = ""
    with open(name, "r") as file:
        try:
            lines = file.read()
        except UnicodeDecodeError:
            print("Error: " + name + " contains characters not in UTF-8. "
                  "Should this be considered a generated file?")
            return False

    file_changed = False

    # The success flag is aggregated across multiple file processing results
    all_success = True

    for subtask in task_pipeline:
        if subtask.should_process_file(config_file, name):
            lines, changed, success = subtask.run_pipeline(
                config_file, name, lines)
            file_changed |= changed
            all_success &= success

    if file_changed:
        with open(name, "wb") as file:
            file.write(lines.encode())

        # After file is written, reset file_changed flag
        file_changed = False

    return all_success


def proc_batch(files):
    """Runs each task in the pipeline on batches of files.

    These tasks read and write to the files directly. They are given a list of
    all files at once to avoid spawning too many subprocesses.
    """
    all_success = True

    for subtask in task_pipeline:
        work = []
        for name in files:
            config_file = Config(os.path.dirname(name), ".styleguide")
            if subtask.should_process_file(config_file, name):
                work.append(name)

        if work:
            if verbose1 or verbose2:
                print("Running", type(subtask).__name__)
                if verbose2:
                    for name in work:
                        print("  on", name)

            all_success &= subtask.run_batch(config_file, work)

    return all_success


def run_pipeline(task_pipeline, args, files):
    """Spawns process pool for proc_pipeline()."""
    init_args = (task_pipeline, args.verbose1, args.verbose2)

    with mp.Pool(args.jobs, proc_init, init_args) as pool:
        # Start worker processes for task pipeline
        results = pool.map(proc_pipeline, files)

        if not all(results):
            sys.exit(1)


def run_batch(task_pipeline, args, file_batches):
    """Spawns process pool for proc_batch()."""
    init_args = (task_pipeline, args.verbose1, args.verbose2)

    with mp.Pool(args.jobs, proc_init, init_args) as pool:
        # Start worker processes for batch tasks
        results = pool.map(proc_batch, file_batches)

        if not all(results):
            sys.exit(1)


def main():
    if not in_git_repo("."):
        print("Error: not invoked within a Git repository", file=sys.stderr)
        sys.exit(1)

    # All file paths are relative to Git repo root directory, so find the root.
    # We can assume the ".git" exists because we already checked we are in a Git
    # repo. Checking "len(directory) > 0" isn't necessary.
    root_path = ""
    git_dir_found = False
    directory = os.getcwd()
    while not git_dir_found:
        git_location = directory + os.sep + ".git"

        # ".git" can be a directory or a file within Git submodules
        if os.path.exists(git_location):
            git_dir_found = True
            if root_path == "":
                root_path = "."
        else:
            directory = directory[:directory.rfind(os.sep)]
            if root_path == "":
                root_path += ".."
            else:
                root_path += os.sep + ".."

    # Delete temporary files from previous incomplete run
    files = [
        os.path.join(dp, f) for dp, dn, fn in os.walk(root_path) for f in fn
        if f.endswith(".tmp")
    ]
    for f in files:
        os.remove(f)

    # Recursively create list of files in given directory
    files = [
        os.path.join(dp, f) for dp, dn, fn in os.walk(root_path) for f in fn
    ]

    if not files:
        print("Error: no files found to format", file=sys.stderr)
        sys.exit(1)

    # Convert relative paths of files to absolute paths
    files = [os.path.abspath(name) for name in files]

    # Don't run tasks on Git metadata
    files = [name for name in files if os.sep + ".git" + os.sep not in name]

    # Don't check for changes in or run tasks on ignored files
    files = filter_ignored_files(files)

    # Create list of all changed files
    changed_file_list = []
    proc = subprocess.Popen(
        ["git", "diff", "--name-only", "master"], stdout=subprocess.PIPE)
    for line in proc.stdout:
        changed_file_list.append(root_path + os.sep +
                                 line.strip().decode("ascii"))

    # Don't run tasks on modifiable or generated files
    work = []
    for name in files:
        config_file = Config(os.path.dirname(name), ".styleguide")

        if config_file.is_modifiable_file(name):
            continue
        if config_file.is_generated_file(name):
            # Emit warning if a generated file was editted
            if name in changed_file_list:
                print("Warning: generated file '" + name + "' modified")
            continue

        work.append(name)
    files = work

    # If there are no files left, do nothing
    if len(files) == 0:
        sys.exit(0)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description=
        "Runs all formatting tasks on the code base. This should be invoked from a directory within the project."
    )
    parser.add_argument(
        "-v",
        dest="verbose1",
        action="store_true",
        help="verbosity level 1 (prints names of processed files)")
    parser.add_argument(
        "-vv",
        dest="verbose2",
        action="store_true",
        help=
        "verbosity level 2 (prints names of processed files and tasks run on them)"
    )
    parser.add_argument(
        "-j",
        dest="jobs",
        type=int,
        default=mp.cpu_count(),
        help="number of jobs to run (default is number of cores)")
    parser.add_argument(
        "-y",
        dest="year",
        type=int,
        default=date.today().year,
        help=
        "year to use when updating license headers (default is current year)")
    parser.add_argument(
        "-clang",
        dest="clang_version",
        type=str,
        default="",
        help=
        "version suffix for clang-format (invokes \"clang-format-CLANG_VERSION\" or \"clang-format\" if no suffix provided)"
    )
    args = parser.parse_args()

    # Prepare file batches for batch tasks
    chunksize = math.ceil(len(files) / args.jobs)
    file_batches = [
        files[i:i + chunksize] for i in range(0, len(files), chunksize)
    ]

    # IncludeOrder is run after Stdlib so any C std headers changed to C++ or
    # vice versa are sorted properly. ClangFormat is run after the other tasks
    # so it can clean up their formatting.
    task_pipeline = [
        LicenseUpdate(str(args.year)),
        Namespace(),
        Newline(),
        Stdlib(),
        IncludeOrder(),
        Whitespace()
    ]
    run_pipeline(task_pipeline, args, files)

    # Lint is run last since previous tasks can affect its output.
    task_pipeline = [
        ClangFormat(args.clang_version),
        PyFormat(),
        Lint(get_repo_root())
    ]
    run_batch(task_pipeline, args, file_batches)


if __name__ == "__main__":
    main()
