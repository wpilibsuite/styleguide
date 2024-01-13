"""This task runs clang-format on the file."""

from subprocess import Popen, PIPE
import sys

import clang_format

from wpiformat.task import PipelineTask


class ClangFormat(PipelineTask):
    def __init__(self, clang_version):
        """Constructor for ClangFormat task.

        Keyword arguments:
        clang_version -- version number of clang-format appended to executable
                         name (deprecated for removal)
        """
        super().__init__()

        if clang_version == "":
            self.exec_name = clang_format._get_executable("clang-format")
        else:
            self.exec_name = "clang-format-" + clang_version

    @staticmethod
    def should_process_file(config_file, name):
        return config_file.is_c_file(name) or config_file.is_cpp_file(name)

    def run_pipeline(self, config_file, name, lines):
        try:
            p = Popen(
                [self.exec_name, "-style=file", "-assume-filename=" + name, "-"],
                stdin=PIPE,
                stdout=PIPE,
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
