#!/usr/bin/env python3

import argparse
from datetime import date
from functools import partial
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


def proc_init(lock):
    global print_lock
    print_lock = lock


def proc_func(verbose1, verbose2, year, clang_version, changed_file_list,
              repo_root, name):
    config_file = Config(os.path.dirname(name), ".styleguide")

    if config_file.is_modifiable_file(name) or ".git" + os.sep in name:
        return True

    if config_file.is_generated_file(name):
        # Emit warning if a generated file was editted
        if name in changed_file_list:
            print("Warning: generated file '" + name + "' modified")
        return True

    # IncludeOrder is run after Stdlib so any C std headers changed to C++ or
    # vice versa are sorted properly. ClangFormat is run after the other tasks
    # so it can clean up their formatting.
    task_pipeline = [
        LicenseUpdate(year),
        Namespace(),
        Newline(),
        Stdlib(),
        IncludeOrder(),
        Whitespace()
    ]

    # These tasks read and write to the files directly. They are given a list of
    # all files at once to avoid spawning too many subprocesses. Lint is run
    # last since previous tasks can affect its output.
    final_tasks = [ClangFormat(clang_version), PyFormat(), Lint(repo_root)]

    # The success flag is aggregated across multiple file processing results
    all_success = True

    if verbose1 or verbose2:
        with print_lock:
            print("Processing", name)
            if verbose2:
                for subtask in task_pipeline:
                    if subtask.should_process_file(config_file, name):
                        print("  with " + type(subtask).__name__)
                for subtask in final_tasks:
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

    for subtask in task_pipeline:
        if subtask.should_process_file(config_file, name):
            lines, changed, success = subtask.run(config_file, name, lines)
            file_changed |= changed
            all_success &= success

    if file_changed:
        with open(name, "wb") as file:
            file.write(lines.encode())

        # After file is written, reset file_changed flag
        file_changed = False

    for subtask in final_tasks:
        if subtask.should_process_file(config_file, name):
            all_success &= subtask.run_all(config_file, [name])

    return all_success


def main():
    if not in_git_repo("."):
        print("Error: not invoked within a Git repository", file=sys.stderr)
        sys.exit(1)

    # All file paths are relative to Git repo root directory, so find the root.
    # We can assume the ".git" exists because we already checked we are in a Git
    # repo. Checking "len(directory) > 0" isn't necessary.
    config_path = ""
    git_dir_found = False
    directory = os.getcwd()
    while not git_dir_found:
        git_location = directory + os.sep + ".git"

        # ".git" can be a directory or a file within Git submodules
        if os.path.exists(git_location):
            git_dir_found = True
            if config_path == "":
                config_path = "."
        else:
            directory = directory[:directory.rfind(os.sep)]
            if config_path == "":
                config_path += ".."
            else:
                config_path += os.sep + ".."

    # Delete temporary files from previous incomplete run
    files = [
        os.path.join(dp, f)
        for dp, dn, fn in os.walk(os.path.expanduser(config_path)) for f in fn
    ]
    for f in files:
        if f.endswith(".tmp"):
            os.remove(f)

    # Recursively create list of files in given directory
    files = [
        os.path.join(dp, f)
        for dp, dn, fn in os.walk(os.path.expanduser(config_path)) for f in fn
    ]

    if not files:
        print("Error: no files found to format", file=sys.stderr)
        sys.exit(1)

    # Convert relative paths of files to absolute paths
    files = [os.path.abspath(name) for name in files]

    # Don't run tasks on Git metadata
    files = [name for name in files if ".git" + os.sep not in name]

    # Don't check for changes in or run tasks on ignored files
    files = filter_ignored_files(files)

    # If there are no files left, do nothing
    if len(files) == 0:
        sys.exit(0)

    # Create list of all changed files
    changed_file_list = []
    proc = subprocess.Popen(
        ["git", "diff", "--name-only", "master"], stdout=subprocess.PIPE)
    for line in proc.stdout:
        changed_file_list.append(config_path + os.sep +
                                 line.strip().decode("ascii"))

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

    # Start worker processes
    print_lock = mp.Lock()
    with mp.Pool(
            args.jobs, initializer=proc_init, initargs=(print_lock,)) as pool:
        func = partial(proc_func, args.verbose1, args.verbose2,
                       str(args.year), args.clang_version, changed_file_list,
                       get_repo_root())
        results = pool.map(func, files)

        for result in results:
            if result == False:
                sys.exit(1)


if __name__ == "__main__":
    main()
