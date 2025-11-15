"""This task runs clang-format on the file."""

import subprocess
import sys

import clang_format

from wpiformat.config import Config
from wpiformat.task import PipelineTask


class ClangFormat(PipelineTask):
    def __init__(self):
        """Constructor for ClangFormat task."""
        super().__init__()

        self.exec_name = clang_format.get_executable("clang-format")

    @staticmethod
    def should_process_file(config_file: Config, filename: str) -> bool:
        return config_file.is_c_file(filename) or config_file.is_cpp_file(filename)

    def run_pipeline(
        self, config_file: Config, filename: str, lines: str
    ) -> tuple[str, bool]:
        try:
            p = subprocess.Popen(
                [self.exec_name, "-style=file", f"-assume-filename={filename}", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                encoding="utf-8",
            )
            stdout, stderr = p.communicate(input=lines)

            if p.returncode != 0:
                print(
                    f"error: {self.exec_name} returned non-zero exit status {p.returncode}",
                    file=sys.stderr,
                )
                print(stderr, file=sys.stderr)
                return lines, False
        except FileNotFoundError:
            print(
                f"error: {self.exec_name} not found in PATH. Is it installed?",
                file=sys.stderr,
            )
            return lines, False

        return stdout, True
