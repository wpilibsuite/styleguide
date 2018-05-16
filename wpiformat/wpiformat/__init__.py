#!/usr/bin/env python3

import argparse
from datetime import date
import math
import multiprocessing as mp
import os
import subprocess
import sys

from wpiformat.bracecomment import BraceComment
from wpiformat.cidentlist import CIdentList
from wpiformat.clangformat import ClangFormat
from wpiformat.config import Config
from wpiformat.includeguard import IncludeGuard
from wpiformat.includeorder import IncludeOrder
from wpiformat.javaclass import JavaClass
from wpiformat.jni import Jni
from wpiformat.licenseupdate import LicenseUpdate
from wpiformat.lint import Lint
from wpiformat.newline import Newline
from wpiformat.pyformat import PyFormat
from wpiformat.stdlib import Stdlib
from wpiformat.task import Task
from wpiformat.usingdeclaration import UsingDeclaration
from wpiformat.usingnamespacestd import UsingNamespaceStd
from wpiformat.whitespace import Whitespace


def filter_ignored_files(names):
    """Returns list of files not in .gitignore.

    Keyword arguments:
    names -- list of files to filter
    """
    # "git check-ignore" misbehaves when the names are separated by "\r\n" on
    # Windows, so os.linesep isn't used here.
    encoded_names = "\n".join(names).encode()

    output_list = subprocess.run(
        ["git", "check-ignore", "--no-index", "-n", "-v", "--stdin"],
        input=encoded_names,
        stdout=subprocess.PIPE).stdout.decode().split("\n")

    # "git check-ignore" prefixes the names of non-ignored files with "::",
    # wraps names in quotes on Windows, and outputs "\n" line separators on all
    # platforms.
    return [
        name[2:].lstrip().strip("\"").replace("\\\\", "\\")
        for name in output_list
        if name[0:2] == "::"
    ]


def proc_init(task_pipeline_copy, verbose1_copy, verbose2_copy):
    """Common initialization for process pool worker.

    Keyword arguments:
    task_pipeline_copy -- task pipeline
    verbose1_copy -- verbose1 flag
    verbose2_copy -- verbose2 flag
    """
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

    Keyword arguments:
    name -- file name string
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


def chunks(l, max_len):
    """Yield successive chunks from l whose content lengths sum to less than
    max_len.
    """
    out = []
    size = 0
    for i, arg in enumerate(l):
        out.append(arg)
        size += len(arg) + len(" ")
        if i == len(l) - 1 or size + len(l[i + 1]) > max_len:
            yield out
            out = []
            size = 0


def proc_batch(files):
    """Runs each task in the pipeline on batches of files.

    These tasks read and write to the files directly. They are given a list of
    all files at once to avoid spawning too many subprocesses.

    Keyword arguments:
    files -- list of file names

    Returns true if all tasks succeeded.
    """
    all_success = True

    for subtask in task_pipeline:
        work = []
        for name in files:
            config_file = Config(os.path.dirname(name), ".styleguide")
            if subtask.should_process_file(config_file, name):
                work.append(name)

        if work:
            # Conservative estimate for max argument length. 32767 is from the
            # Win32 docs for CreateProcessA(), but the limit appears to be lower
            # than that in practice.
            MAX_WIN32_ARGS_LEN = 32767 * 7 / 8

            for subwork in chunks(work, MAX_WIN32_ARGS_LEN):
                if verbose1 or verbose2:
                    print("Running", type(subtask).__name__)
                    if verbose2:
                        for name in subwork:
                            print("  on", name)
                all_success &= subtask.run_batch(config_file, subwork)

    return all_success


def run_pipeline(task_pipeline, args, files):
    """Spawns process pool for proc_pipeline().

    Keyword arguments:
    task_pipeline -- task pipeline
    args -- command line arguments from argparse
    files -- list of file names to process

    Calls sys.exit(1) if any task fails.
    """
    init_args = (task_pipeline, args.verbose1, args.verbose2)

    with mp.Pool(args.jobs, proc_init, init_args) as pool:
        # Start worker processes for task pipeline
        results = pool.map(proc_pipeline, files)

        if not all(results):
            sys.exit(1)


def run_batch(task_pipeline, args, file_batches):
    """Spawns process pool for proc_batch().

    Keyword arguments:
    task_pipeline -- task pipeline
    args -- command line arguments from argparse
    file_batches -- list of file names to process

    """
    init_args = (task_pipeline, args.verbose1, args.verbose2)

    with mp.Pool(args.jobs, proc_init, init_args) as pool:
        # Start worker processes for batch tasks
        results = pool.map(proc_batch, file_batches)

        if not all(results):
            sys.exit(1)


def main():
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
    parser.add_argument(
        "-f",
        dest="file",
        type=str,
        default="",
        nargs="+",
        help=
        "file or directory names (can be path relative to python invocation directory or absolute path)"
    )
    args = parser.parse_args()

    # All discovered files are relative to Git repo root directory, so find the
    # root.
    root_path = Task.get_repo_root()
    if root_path == "":
        print("Error: not invoked within a Git repository", file=sys.stderr)
        sys.exit(1)

    # If no files explicitly specified
    if not args.file:
        # Delete temporary files from previous incomplete run
        files = [
            os.path.join(dp, f)
            for dp, dn, fn in os.walk(root_path)
            for f in fn
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
    else:
        files = []
        for name in args.file:
            # If a directory was specified, recursively expand it
            if os.path.isdir(name):
                files.extend([
                    os.path.join(dp, f)
                    for dp, dn, fn in os.walk(name)
                    for f in fn
                ])
            else:
                files.append(name)

    # Convert relative paths of files to absolute paths
    files = [os.path.abspath(name) for name in files]

    # Don't run tasks on Git metadata
    files = [name for name in files if os.sep + ".git" + os.sep not in name]

    # Don't check for changes in or run tasks on ignored files
    files = filter_ignored_files(files)

    # Create list of all changed files
    changed_file_list = []

    output_list = subprocess.run(
        ["git", "diff", "--name-only", "master"],
        stdout=subprocess.PIPE).stdout.split()
    for line in output_list:
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

    # Prepare file batches for batch tasks
    chunksize = math.ceil(len(files) / args.jobs)
    file_batches = [
        files[i:i + chunksize] for i in range(0, len(files), chunksize)
    ]

    # IncludeOrder is run after Stdlib so any C std headers changed to C++ or
    # vice versa are sorted properly. ClangFormat is run after the other tasks
    # so it can clean up their formatting.
    task_pipeline = [
        BraceComment(),
        CIdentList(),
        IncludeGuard(),
        LicenseUpdate(str(args.year)),
        JavaClass(),
        Newline(),
        Stdlib(),
        IncludeOrder(),
        UsingDeclaration(),
        UsingNamespaceStd(),
        Whitespace()
    ]
    run_pipeline(task_pipeline, args, files)

    task_pipeline = [ClangFormat(args.clang_version)]
    run_batch(task_pipeline, args, file_batches)

    # These tasks fix clang-format formatting
    task_pipeline = [Jni()]
    run_pipeline(task_pipeline, args, files)

    # Lint is run last since previous tasks can affect its output.
    task_pipeline = [PyFormat(), Lint()]
    run_batch(task_pipeline, args, file_batches)


if __name__ == "__main__":
    main()
