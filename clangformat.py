"""This task runs clang-format on the file."""

import subprocess
import sys

from task import Task


class ClangFormat(Task):

    def get_file_extensions(self):
        return Task.get_config("cExtensions") + \
            Task.get_config("cppHeaderExtensions") + \
            Task.get_config("cppSrcExtensions")

    def run(self, name, lines):
        args = ["-assume-filename=" + name, "-style=file", "-"]
        try:
            proc = subprocess.Popen(
                ["clang-format-3.8"] + args,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE)
            output = proc.communicate(lines.encode())[0]
            output = output.decode()
        except FileNotFoundError:
            try:
                proc = subprocess.Popen(
                    ["clang-format"] + args,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE)
                output = proc.communicate(lines.encode())[0]
                output = output.decode()
            except FileNotFoundError:
                print(
                    "Error: clang-format not found in PATH. Is it installed?",
                    file=sys.stderr)
                return (lines, False, False)

        if lines == output:
            return (lines, False, True)
        else:
            return (output, True, True)
