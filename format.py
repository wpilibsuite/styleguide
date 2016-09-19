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
from newline import Newline
from stdlib import Stdlib
from task import Task
from whitespace import Whitespace

# Check that the current directory is part of a Git repository
def in_git_repo(directory):
    ret = subprocess.run(["git", "rev-parse"], stderr = subprocess.DEVNULL)
    return ret.returncode == 0

def proc_func(work, is_verbose, print_lock):
    # IncludeOrder is run after Stdlib so any C std headers changed to C++ or
    # vice versa are sorted properly. ClangFormat is run after the other tasks
    # so it can clean up their formatting.
    task_pipeline = [LicenseUpdate(), Newline(), Stdlib(), IncludeOrder(),
                     Whitespace(), ClangFormat()]

    # These tasks are performed on files directly. Lint is run last since
    # previous tasks can affect its output.
    final_tasks = [Lint()]

    for name in work:
        if is_verbose:
            with print_lock:
                print("Processing", name)
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
                lines, changed = task.run(name, lines)
                file_changed |= changed

        if file_changed:
            with open(name, "wb") as file:
                file.write(lines.encode())

        for task in final_tasks:
            if task.file_matches_extension(name):
                task.run(name, "")

def main():
    if not in_git_repo("."):
        print("Error: not invoked within a Git repository", file = sys.stderr)
        sys.exit(1)

    # Handle running in either the root or styleguide directories
    config_path = ""
    if os.getcwd().rpartition(os.sep)[2] == "styleguide":
        config_path = ".."
    else:
        config_path = "."

    # Delete temporary files from previous incomplete run
    files = [os.path.join(dp, f) for dp, dn, fn in
             os.walk(os.path.expanduser(config_path)) for f in fn]
    for f in files:
        if f.endswith(".tmp"):
            os.remove(f)

    # Recursively create list of files in given directory
    files = [os.path.join(dp, f) for dp, dn, fn in
             os.walk(os.path.expanduser(config_path)) for f in fn]

    if not files:
        print("Error: no files found to format", file = sys.stderr)
        sys.exit(1)

    # Don't check for changes in or run tasks on modifiable files
    files = [name for name in files if not Task.is_modifiable_file(name)]

    # Create list of all changed files
    changed_file_list = []
    proc = subprocess.Popen(["git", "diff", "--name-only", "master"],
                            stdout = subprocess.PIPE)
    for line in proc.stdout:
        changed_file_list.append(config_path + os.sep +
                               line.strip().decode("ascii"))

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
    parser = argparse.ArgumentParser(description = "Runs all formatting tasks on the code base. This should be invoked from either the styleguide directory or the root directory of the project.")
    parser.add_argument("-v", dest = "verbose", action = "store_true",
                        help = "enable output verbosity")
    parser.add_argument("-j", dest = "jobs", type = int,
                        default = multiprocessing.cpu_count(),
                        help = "number of jobs to run (default is number of cores)")
    args = parser.parse_args()
    jobs = args.jobs
    is_verbose = args.verbose

    processes = []
    print_lock = multiprocessing.Lock()

    # Make list of evenly-sized work chunks
    chunk_size = math.ceil(len(files) / jobs)
    work = [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]

    assert len(work) == jobs

    # Start worker processes
    for i in range(0, jobs):
        proc = multiprocessing.Process(target = proc_func,
                                       args = (work[i], is_verbose, print_lock))
        proc.daemon = True
        proc.start()
        processes.append(proc)

    # Wait for worker processes to finish
    for i in range(0, jobs):
        processes[i].join()

if __name__ == "__main__":
    main()
