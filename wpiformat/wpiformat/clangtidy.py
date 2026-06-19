"""
This task runs clang-tidy.

Runs on: C, C++
"""

import subprocess
import sys
from pathlib import Path

import clang_tidy

from wpiformat.config import Config
from wpiformat.task import StandaloneTask


class ClangTidy(StandaloneTask):
    def __init__(self, compile_commands: str, extra_args: list[str]):
        """Constructor for ClangTidy task.

        Keyword arguments:
        compile_commands -- directory containing compile_commands.json
        extra_args -- list of extra arguments to clang-tidy
        """
        super().__init__()

        self.exec_name = clang_tidy._get_executable("clang-tidy")

        self.args = ["--quiet"]
        if compile_commands:
            self.args += ["-p", compile_commands]

        # Prepend a dash to the argument here because the main argument parser
        # treats strings with a dash prefix as a new argument instead of the
        # value for -extra-args
        for arg in extra_args:
            self.args += ["-extra-arg", "-" + arg]

    @staticmethod
    def should_process_file(config_file: Config, filename: Path) -> bool:
        return config_file.is_cpp_file(filename)

    def run_standalone(self, config_file: Config, filename: Path) -> bool:
        try:
            stdout = subprocess.run(
                [self.exec_name] + self.args + [filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                check=False,
            ).stdout
        except FileNotFoundError:
            print(
                f"error: {self.exec_name} not found in PATH. Is it installed?",
                file=sys.stderr,
            )
            return False

        lines = [line for line in stdout.rstrip().split("\n") if line]

        # Filter out "X error(s) and Y warning(s) generated." lines
        lines = [line for line in lines if " generated." not in line]

        # Filter out "Error while processing" lines
        lines = [line for line in lines if "Error while processing" not in line]

        # Filter out "Processing file" lines
        lines = [line for line in lines if "Processing file" not in line]

        # Ignore include file not found errors
        filtered_lines = []
        iterlines = iter(lines)
        for line in iterlines:
            if "file not found [clang-diagnostic-error]" in line:
                # Skip #include line and caret indicator line
                next(iterlines)
                next(iterlines)
            else:
                filtered_lines.append(line)
        lines = filtered_lines

        # If any lines are non-empty, print them and report an error
        if any(len(line.rstrip()) > 0 for line in lines):
            print(f"== clang-tidy {filename} ==\n" + "\n".join(lines))
            return False

        return True
