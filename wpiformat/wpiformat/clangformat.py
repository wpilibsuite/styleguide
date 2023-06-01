"""This task runs clang-format on the file."""

from subprocess import Popen, PIPE
import sys

import clang_format

from wpiformat.task import Task


class ClangFormat(Task):
    @staticmethod
    def should_process_file(config_file, name):
        return config_file.is_c_file(name) or config_file.is_cpp_file(name)

    def run_pipeline(self, config_file, name, lines):
        args = ["-style=file", "-assume-filename=" + name, "-"]
        p = Popen(
            [clang_format._get_executable("clang-format")] + args,
            encoding="utf-8",
            stdin=PIPE,
            stdout=PIPE,
        )
        output = p.communicate(input=lines)[0]

        return output, True
