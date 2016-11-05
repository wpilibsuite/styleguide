#!/usr/bin/env python3

import argparse
import math
import multiprocessing
import os
import subprocess
import sys

from clangformat import ClangFormat
from includeorder import IncludeOrder
from licenseupdate import LicenseUpdate
from lint import Lint
from namespace import Namespace
from newline import Newline
from pyformat import PyFormat
from stdlib import Stdlib
from task import Task
from whitespace import Whitespace


# Check that the current directory is part of a Git repository
def in_git_repo(directory):
    cmd = ["git", "rev-parse"]
    returncode = subprocess.call(cmd, stderr=subprocess.DEVNULL)
    return returncode == 0


def proc_func(procnum, work, verbose1, verbose2, print_lock, ret_dict):
    # IncludeOrder is run after Stdlib so any C std headers changed to C++ or
    # vice versa are sorted properly. ClangFormat is run after the other tasks
    # so it can clean up their formatting.
    task_pipeline = [
        LicenseUpdate(), Namespace(), Newline(), Stdlib(), IncludeOrder(),
        Whitespace(), ClangFormat()
    ]

    # These tasks are performed on files directly. Lint is run last since
    # previous tasks can affect its output.
    final_tasks = [PyFormat(), Lint()]

    # The success flag is aggregated across multiple file processing results
    ret_dict[procnum] = True

    for name in work:
        if verbose1 or verbose2:
            with print_lock:
                print("Processing", name)
                if verbose2:
                    for task in task_pipeline:
                        if task.file_matches_extension(name):
                            print("  with " + type(task).__name__)
                    for task in final_tasks:
                        if task.file_matches_extension(name):
                            print("  with " + type(task).__name__)

        lines = ""
        with open(name, "r") as file:
            lines = file.read()
        file_changed = False

        for task in task_pipeline:
            if task.file_matches_extension(name):
                lines, changed, success = task.run(name, lines)
                file_changed |= changed
                ret_dict[procnum] &= success

        if file_changed:
            with open(name, "wb") as file:
                file.write(lines.encode())

            # After file is written, reset file_changed flag
            file_changed = False

        for task in final_tasks:
            if task.file_matches_extension(name):
                lines, file_changed, success = task.run(name, "")
                ret_dict[procnum] &= success

                # Since these tasks read from the file instead of the pipeline,
                # any changes made by the previous task should be written to the
                # file before running the next task.
                if file_changed:
                    with open(name, "wb") as file:
                        file.write(lines.encode())

                    # After file is written, reset file_changed flag
                    file_changed = False


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

    # Don't check for changes in or run tasks on modifiable files
    files = [name for name in files if not Task.is_modifiable_file(name)]

    # Create list of all changed files
    changed_file_list = []
    proc = subprocess.Popen(
        ["git", "diff", "--name-only", "master"], stdout=subprocess.PIPE)
    for line in proc.stdout:
        changed_file_list.append(config_path + os.sep + line.strip().decode(
            "ascii"))

    # Emit warning if a generated file was editted
    for name in files:
        if Task.is_generated_file(name) and name in changed_file_list:
            print("Warning: generated file '" + name + "' modified")

    # Don't format generated files
    files = [name for name in files if not Task.is_generated_file(name)]

    # If there are no files left, do nothing
    if len(files) == 0:
        sys.exit(0)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Runs all formatting tasks on the code base. This should be invoked from a directory within the project."
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
        help="verbosity level 2 (prints names of processed files and tasks run on them)"
    )
    parser.add_argument(
        "-j",
        dest="jobs",
        type=int,
        default=multiprocessing.cpu_count(),
        help="number of jobs to run (default is number of cores)")
    args = parser.parse_args()
    verbose1 = args.verbose1
    verbose2 = args.verbose2
    jobs = args.jobs

    processes = []
    print_lock = multiprocessing.Lock()
    manager = multiprocessing.Manager()

    # Make list of evenly-sized work chunks
    chunk_size = math.ceil(len(files) / jobs)
    work = [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]

    assert len(work) <= jobs

    # If there isn't enough work for all work queues, decrease number of jobs
    if len(work) < jobs:
        jobs = len(work)

    # Start worker processes
    ret_dict = manager.dict()
    for i in range(0, jobs):
        proc = multiprocessing.Process(
            target=proc_func,
            args=(i, work[i], verbose1, verbose2, print_lock, ret_dict))
        proc.daemon = True
        proc.start()
        processes.append(proc)

    # Wait for worker processes to finish
    for i in range(0, jobs):
        processes[i].join()

    success = True
    for i in range(0, jobs):
        success &= ret_dict[i]

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
