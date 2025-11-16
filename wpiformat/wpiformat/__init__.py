#!/usr/bin/env python3

import argparse
import math
import multiprocessing as mp
import os
import subprocess
import sys
from typing import Any, Generator

from wpiformat.bracecomment import BraceComment
from wpiformat.cidentlist import CIdentList
from wpiformat.clangformat import ClangFormat
from wpiformat.clangtidy import ClangTidy
from wpiformat.cmakeformat import CMakeFormat
from wpiformat.config import Config
from wpiformat.eofnewline import EofNewline
from wpiformat.gtestname import GTestName
from wpiformat.includeguard import IncludeGuard
from wpiformat.javaclass import JavaClass
from wpiformat.jni import Jni
from wpiformat.licenseupdate import LicenseUpdate
from wpiformat.lint import Lint
from wpiformat.pyformat import PyFormat
from wpiformat.task import BatchTask, PipelineTask, StandaloneTask, Task
from wpiformat.usingdeclaration import UsingDeclaration
from wpiformat.usingnamespacestd import UsingNamespaceStd
from wpiformat.whitespace import Whitespace


def filter_ignored_files(filenames: list[str]) -> list[str]:
    """Returns list of files not in .gitignore.

    Keyword arguments:
    filenames -- list of filenames to filter
    """
    # "git check-ignore" misbehaves when the names are separated by "\r\n" on
    # Windows, so os.linesep isn't used here.
    proc = subprocess.run(
        ["git", "check-ignore", "--no-index", "-n", "-v", "--stdin"],
        input="\n".join(filenames).encode(),
        stdout=subprocess.PIPE,
    )
    if proc.returncode == 128:
        raise subprocess.CalledProcessError(
            proc.returncode, proc.args, proc.stdout, proc.stderr
        )

    # "git check-ignore" prefixes the names of non-ignored files with "::",
    # wraps names in quotes on Windows, and outputs "\n" line separators on all
    # platforms.
    return [
        filename[2:].lstrip().strip('"').replace("\\\\", "\\")
        for filename in proc.stdout.decode().split("\n")
        if filename[0:2] == "::"
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


def proc_pipeline(filename: str) -> bool:
    """Runs the contents of each file through the task pipeline.

    If the contents were modified at any point, the result is written back out
    to the file.

    Keyword arguments:
    filename -- filename
    """
    # TODO: Remove handling for deprecated .styleguide file
    try:
        config_file = Config(os.path.dirname(filename), ".wpiformat")
    except OSError:
        config_file = Config(os.path.dirname(filename), ".styleguide")

    if verbose1 or verbose2:
        with print_lock:
            print("Processing", filename)
            if verbose2:
                print("  with config " + config_file.filename)
                for subtask in task_pipeline:
                    if subtask.should_process_file(config_file, filename):
                        print("  with " + type(subtask).__name__)

    lines = ""
    with open(filename, "r", encoding="utf8") as file:
        try:
            lines = file.read()
        except UnicodeDecodeError:
            print(
                f"error: {filename} contains characters not in UTF-8. Should this be considered a generated file?"
            )
            return False

    # The success flag is aggregated across multiple file processing results
    all_success = True

    output = lines
    for subtask in task_pipeline:
        if subtask.should_process_file(config_file, filename):
            output, success = subtask.run_pipeline(config_file, filename, output)
            all_success &= success

    if lines != output:
        with open(filename, "wb") as file:
            file.write(output.encode())

    return all_success


def proc_standalone(filename: str) -> bool:
    """Runs each task on each file.

    Keyword arguments:
    filename -- filename
    """
    # TODO: Remove handling for deprecated .styleguide file
    try:
        config_file = Config(os.path.dirname(filename), ".wpiformat")
    except OSError:
        config_file = Config(os.path.dirname(filename), ".styleguide")

    if verbose2:
        with print_lock:
            print("Processing", filename)
            for subtask in task_pipeline:
                if subtask.should_process_file(config_file, filename):
                    print("  with " + type(subtask).__name__)

    # The success flag is aggregated across multiple file processing results
    all_success = True

    for subtask in task_pipeline:
        if subtask.should_process_file(config_file, filename):
            success = subtask.run_standalone(config_file, filename)
            all_success &= success

    return all_success


def chunks(l: list[Any], max_len: int) -> Generator[list[Any], None, None]:
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


def proc_batch(filenames: list[str]) -> bool:
    """Runs each task in the pipeline on batches of files.

    These tasks read and write to the files directly. They are given a list of
    all files at once to avoid spawning too many subprocesses.

    Keyword arguments:
    filenames -- list of filenames

    Returns true if all tasks succeeded.
    """
    all_success = True

    for subtask in task_pipeline:
        work = []
        for filename in filenames:
            # TODO: Remove handling for deprecated .styleguide file
            try:
                config_file = Config(os.path.dirname(filename), ".wpiformat")
            except OSError:
                config_file = Config(os.path.dirname(filename), ".styleguide")

            if subtask.should_process_file(config_file, filename):
                work.append(filename)

        if work:
            # Conservative estimate for max argument length. 32767 is from the
            # Win32 docs for CreateProcessA(), but the limit appears to be lower
            # than that in practice.
            MAX_WIN32_ARGS_LEN = int(32767 * 7 / 8)

            for subwork in chunks(work, MAX_WIN32_ARGS_LEN):
                if verbose1 or verbose2:
                    print("Running", type(subtask).__name__)
                    if verbose2:
                        for name in subwork:
                            print("  on", name)
                all_success &= subtask.run_batch(config_file, subwork)

    return all_success


def run_pipeline(task_pipeline, args, filenames: list[str]):
    """Spawns process pool for proc_pipeline().

    Keyword arguments:
    task_pipeline -- task pipeline
    args -- command line arguments from argparse
    filenames -- list of filenames to process

    Calls sys.exit(1) if any task fails.
    """
    init_args = (task_pipeline, args.verbose1, args.verbose2)

    # Check tasks are all pipeline tasks
    invalid_tasks = [
        type(task).__name__
        for task in task_pipeline
        if not issubclass(type(task), PipelineTask)
    ]
    if invalid_tasks:
        print(f"error: the following pipeline tasks are invalid: {invalid_tasks}")
        sys.exit(1)

    with mp.Pool(args.jobs, proc_init, init_args) as pool:
        # Start worker processes for task pipeline
        results = pool.map(proc_pipeline, filenames)

        if not all(results):
            sys.exit(1)


def run_batch(task_pipeline, args, filename_batches: list[list[str]]):
    """Spawns process pool for proc_batch().

    Keyword arguments:
    task_pipeline -- task pipeline
    args -- command line arguments from argparse
    filename_batches -- list of batches of filenames to process

    Calls sys.exit(1) if any task fails.
    """
    init_args = (task_pipeline, args.verbose1, args.verbose2)

    # Check tasks are all batch tasks
    invalid_tasks = [
        type(task).__name__
        for task in task_pipeline
        if not issubclass(type(task), BatchTask)
    ]
    if invalid_tasks:
        print(f"error: the following batch tasks are invalid: {invalid_tasks}")
        sys.exit(1)

    with mp.Pool(args.jobs, proc_init, init_args) as pool:
        # Start worker processes for batch tasks
        results = pool.map(proc_batch, filename_batches)

        if not all(results):
            sys.exit(1)


def run_standalone(task_pipeline, args, filenames: list[str]):
    """Spawns process pool for proc_standalone().

    Keyword arguments:
    task_pipeline -- task pipeline
    args -- command line arguments from argparse
    filenames -- list of filenames to process

    Calls sys.exit(1) if any task fails.
    """
    init_args = (task_pipeline, args.verbose1, args.verbose2)

    # Check tasks are all standalone tasks
    invalid_tasks = [
        type(task).__name__
        for task in task_pipeline
        if not issubclass(type(task), StandaloneTask)
    ]
    if invalid_tasks:
        print(f"error: the following standalone tasks are invalid: {invalid_tasks}")
        sys.exit(1)

    with mp.Pool(args.jobs, proc_init, init_args) as pool:
        # Start worker processes for standalone tasks
        results = pool.map(proc_standalone, filenames)

        if not all(results):
            sys.exit(1)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Runs all formatting tasks on the code base. This should be invoked from a directory within the project."
    )
    parser.add_argument(
        "-v",
        dest="verbose1",
        action="store_true",
        help="verbosity level 1 (prints names of processed files)",
    )
    parser.add_argument(
        "-vv",
        dest="verbose2",
        action="store_true",
        help="verbosity level 2 (prints names of processed files and tasks run on them)",
    )
    list_files_group = parser.add_mutually_exclusive_group()
    list_files_group.add_argument(
        "-list-all-files",
        dest="list_all_files",
        action="store_true",
        help="list files to be processed instead of processing them",
    )
    list_files_group.add_argument(
        "-list-changed-files",
        dest="list_changed_files",
        action="store_true",
        help="same as -list-all-files, but list only files changed from default branch",
    )
    parser.add_argument(
        "-default-branch",
        dest="default_branch",
        type=str,
        default="",
        help="branch with respect to which changed files list is generated",
    )
    # mp.Pool() uses WaitForMultipleObjects() to wait for subprocess completion
    # on Windows. WaitForMultipleObjects() cannot wait on more then 64 events at
    # once, and mp uses a few internal events. Therefore, the maximum number of
    # parallel jobs is 60.
    cpu_count = mp.cpu_count()
    if sys.platform == "win32":
        cpu_count = min(cpu_count, 60)
    parser.add_argument(
        "-j",
        dest="jobs",
        type=int,
        default=cpu_count,
        help="number of jobs to run (default is number of cores)",
    )
    tidy_group = parser.add_mutually_exclusive_group()
    tidy_group.add_argument(
        "-tidy-changed",
        dest="tidy_changed",
        action="store_true",
        help="also runs clang-tidy-CLANG_VERSION on changed files; this requires a compile_commands.json file",
    )
    tidy_group.add_argument(
        "-tidy-all",
        dest="tidy_all",
        action="store_true",
        help="also runs clang-tidy-CLANG_VERSION on all files (this takes a while); this requires a compile_commands.json file",
    )
    parser.add_argument(
        "-compile-commands",
        dest="compile_commands",
        type=str,
        default="",
        help="path to directory containing compile_commands.json; if unset will search in parent paths",
    )
    parser.add_argument(
        "-tidy-extra-args",
        dest="tidy_extra_args",
        type=str,
        default="",
        help='a comma-delimited list of extra arguments for clang-tidy (given "ARG1,ARG2", invokes "clang-tidy -extra-arg -ARG1 -extra-arg -ARG2")',
    )
    parser.add_argument(
        "-f",
        dest="file",
        type=str,
        default="",
        nargs="+",
        help="file or directory names (can be path relative to python invocation directory or absolute path)",
    )
    parser.add_argument(
        "-no-format",
        dest="no_format",
        action="store_true",
        help="disable formatting steps, only run linting",
    )
    args = parser.parse_args()

    # tidy requires compile_commands.json
    if args.tidy_all or args.tidy_changed:
        ccloc = os.path.join(args.compile_commands, "compile_commands.json")
        if not os.path.exists(ccloc):
            print(
                f"error: clang-tidy: {ccloc} not found (try -compile-commands)",
                file=sys.stderr,
            )
            sys.exit(1)

    # All discovered files are relative to Git repo root directory, so find the
    # root.
    root_path = Task.get_repo_root()
    if root_path == "":
        print("error: not invoked within a Git repository", file=sys.stderr)
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
        files = [os.path.join(dp, f) for dp, dn, fn in os.walk(root_path) for f in fn]

        if not files:
            print("error: no files found to format", file=sys.stderr)
            sys.exit(1)
    else:
        files = []
        for name in args.file:
            # If a directory was specified, recursively expand it
            if os.path.isdir(name):
                files.extend(
                    [os.path.join(dp, f) for dp, dn, fn in os.walk(name) for f in fn]
                )
            else:
                files.append(name)

    # Convert relative paths of files to absolute paths
    files = [os.path.abspath(name) for name in files]

    # Don't run tasks on Git metadata
    files = [name for name in files if os.sep + ".git" + os.sep not in name]

    # Don't check for changes in or run tasks on ignored files
    files = filter_ignored_files(files)

    # Throw an error if any files or directories don't exist
    for f in files:
        if not os.path.exists(f):
            if not os.path.islink(f):
                print(f"error: {f}: No such file or directory")
                sys.exit(1)
            else:
                print(f"warning: {f}: Broken symlink")

    # Determine name of default branch for generated file comparisons
    if not (default_branch := args.default_branch):
        branch_options = ["origin/HEAD", "main", "master"]
        for branch in branch_options:
            proc = subprocess.run(
                ["git", "rev-parse", "-q", "--verify", branch],
                stdout=subprocess.DEVNULL,
            )
            if proc.returncode == 0:
                default_branch = branch
                break
        if not default_branch:
            print(
                f"error: no default branch provided, and none of the following default branches exist: {branch_options}."
            )
            sys.exit(1)

    # Create list of all changed files
    changed_file_list = [
        root_path + os.sep + os.path.normpath(line.rstrip())
        for line in subprocess.check_output(
            ["git", "diff", "--name-only", f"{default_branch}..."], encoding="ascii"
        ).split()
    ]

    # Don't run tasks on modifiable or generated files
    work = []
    for name in files:
        # TODO: Remove handling for deprecated .styleguide file
        try:
            config_file = Config(os.path.dirname(name), ".wpiformat")
        except OSError:
            config_file = Config(os.path.dirname(name), ".styleguide")

        if config_file.is_modifiable_file(name):
            continue
        if config_file.is_generated_file(name):
            # Emit warning if a generated file was editted
            if (
                name in changed_file_list
                and not args.list_all_files
                and not args.list_changed_files
            ):
                print("warning: generated file '" + name + "' modified")
            continue

        work.append(name)
    files = work

    # If there are no files left, do nothing
    if len(files) == 0:
        sys.exit(0)

    # Handle list-all-files and list-changed-files options
    if args.list_all_files or args.list_changed_files:
        if args.list_changed_files:
            files = list(set(files) & set(changed_file_list))
        for file in files:
            print(file)
        sys.exit(0)

    # Prepare file batches for batch tasks
    chunksize = math.ceil(len(files) / args.jobs)
    file_batches = [files[i : i + chunksize] for i in range(0, len(files), chunksize)]

    if args.no_format:
        # Only run Lint
        task_pipeline = [Lint()]
        run_batch(task_pipeline, args, file_batches)
    else:
        # ClangFormat is run after the other tasks so it can clean up their
        # formatting.
        task_pipeline = [
            BraceComment(),
            CIdentList(),
            EofNewline(),
            GTestName(),
            IncludeGuard(),
            LicenseUpdate(),
            JavaClass(),
            UsingDeclaration(),
            UsingNamespaceStd(),
            Whitespace(),
            ClangFormat(),
            Jni(),  # Fixes clang-format formatting
        ]
        run_pipeline(task_pipeline, args, files)

        # Lint is run last since previous tasks can affect its output.
        task_pipeline = [CMakeFormat(), PyFormat(), Lint()]

        run_batch(task_pipeline, args, file_batches)

    # ClangTidy is run last of all; it needs the actual files
    if args.tidy_all or args.tidy_changed:
        if args.tidy_changed:
            files = list(set(files) & set(changed_file_list))
        task_pipeline = [
            ClangTidy(
                args.compile_commands,
                args.tidy_extra_args.split(",") if args.tidy_extra_args else [],
            )
        ]
        run_standalone(task_pipeline, args, files)


if __name__ == "__main__":
    main()
