"""This task runs clang-format on the file."""

import subprocess
import sys

from wpiformat.task import Task


class ClangFormat(Task):

    def __init__(self, clang_version):
        """Constructor for ClangFormat task.

        Keyword arguments:
        clang_version -- version number of clang-format appended to executable
                         name
        """
        Task.__init__(self)

        if clang_version == "":
            self.exec_name = "clang-format"
        else:
            self.exec_name = "clang-format-" + clang_version

    def should_process_file(self, config_file, name):
        return config_file.is_c_file(name) or config_file.is_cpp_file(name)

    def run_batch(self, config_file, names):
        args = ["-style=file", "-i"] + names
        try:
            returncode = subprocess.run([self.exec_name] + args).returncode
        except FileNotFoundError:
            print(
                "Error: " + self.exec_name +
                " not found in PATH. Is it installed?",
                file=sys.stderr)
            return False
        return returncode == 0
