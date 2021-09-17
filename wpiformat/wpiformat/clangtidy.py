"""This task runs clang-tidy on the file."""

import subprocess
import sys

from wpiformat.task import Task


class ClangTidy(Task):

    def __init__(self, clang_version, compile_commands):
        """Constructor for ClangTidy task.

        Keyword arguments:
        clang_version -- version number of clang-tidy appended to executable
                         name
        compile_commands -- directory containing compile_commands.json
        """
        super().__init__()

        if clang_version == "":
            self.exec_name = "clang-tidy"
        else:
            self.exec_name = "clang-tidy-" + clang_version

        self.args = ["--quiet"]
        if compile_commands:
            self.args += ["-p", compile_commands]

    @staticmethod
    def should_process_file(config_file, name):
        return config_file.is_cpp_file(name)

    def run_standalone(self, config_file, name):
        try:
            output = subprocess.run([self.exec_name] + self.args + [name],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    encoding="utf-8").stdout
        except FileNotFoundError:
            print("Error: " + self.exec_name +
                  " not found in PATH. Is it installed?",
                  file=sys.stderr)
            return False

        lines = [l for l in output.split('\n') if l]

        # ignore include file not found errors at beginning
        if lines and "file not found [clang-diagnostic-error]" in lines[0]:
            lines = lines[3:]

        if lines:
            print("== clang-tidy " + name + " ==")
            print('\n'.join(lines))
            return False

        return True
