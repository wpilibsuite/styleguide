"""This task runs cpplint.py on a C++ source file."""

import os
import sys
from contextlib import redirect_stdout

import cpplint

from wpiformat.config import Config
from wpiformat.task import BatchTask


class Lint(BatchTask):
    @staticmethod
    def should_process_file(config_file: Config, filename: str) -> bool:
        return config_file.is_cpp_file(filename)

    @staticmethod
    def run_batch(config_file: Config, filenames: list[str]) -> bool:
        # Prepare arguments to cpplint.py
        saved_argv = sys.argv

        exclusion_filters = [
            "build/c++11",
            "build/c++17",
            "build/header_guard",
            "build/include_order",
            "build/include_subdir",
            "build/namespaces",
            "legal/copyright",
            "readability/braces",
            "readability/check",
            "readability/todo",
            "runtime/references",
            "runtime/string",
            "whitespace/braces",
            "whitespace/comma",
            "whitespace/comments",
            "whitespace/end_of_line",
            "whitespace/ending_newline",
            "whitespace/indent",
            "whitespace/indent_namespace",
            "whitespace/line_length",
            "whitespace/newline",
            "whitespace/operators",
            "whitespace/parens",
            "whitespace/semicolon",
            "whitespace/tab",
        ]

        # Prepare header file extensions
        header_exts = []
        for pattern in config_file.group("cHeaderFileInclude") + config_file.group(
            "cppHeaderFileInclude"
        ):
            basename = os.path.basename(pattern)
            header_exts.append(basename[basename.rfind(".") + 1 :].rstrip("$"))

        args = ["cpplint.py", "--filter=-" + ",-".join(exclusion_filters)]
        if header_exts:
            args.append("--headers=" + ",".join(header_exts))
        args.append("--quiet")
        sys.argv = args + filenames

        # Run cpplint.py
        try:
            with open(os.devnull, "w") as devnull, redirect_stdout(devnull):
                cpplint.main()
        except SystemExit as e:
            # Restore original arguments
            sys.argv = saved_argv

            # Report success if error code is 0 (False)
            return e.code == False
        return False
