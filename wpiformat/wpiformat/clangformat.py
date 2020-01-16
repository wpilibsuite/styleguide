"""This task runs clang-format on the file."""

from subprocess import Popen, PIPE
import sys

from wpiformat.task import Task


class ClangFormat(Task):

    def __init__(self, clang_version):
        """Constructor for ClangFormat task.

        Keyword arguments:
        clang_version -- version number of clang-format appended to executable
                         name
        """
        super().__init__()

        if clang_version == "":
            self.exec_name = "clang-format"
        else:
            self.exec_name = "clang-format-" + clang_version

    def should_process_file(self, config_file, name):
        return config_file.is_c_file(name) or config_file.is_cpp_file(name)

    def run_pipeline(self, config_file, name, lines):
        args = ["-style=file", "-assume-filename=" + name, "-"]
        try:
            p = Popen([self.exec_name] + args,
                      encoding="utf-8",
                      stdin=PIPE,
                      stdout=PIPE)
            output = p.communicate(input=lines)[0]
        except FileNotFoundError:
            print("Error: " + self.exec_name +
                  " not found in PATH. Is it installed?",
                  file=sys.stderr)
            return (lines, False)

        return (output, True)
