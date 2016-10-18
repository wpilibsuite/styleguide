"""This task runs yapf on files with Python extension."""

import subprocess
import sys

from task import Task


class PyFormat(Task):

    def get_file_extensions(self):
        return ["py"]

    def run(self, name, lines):
        args = ["yapf", "--style", "google", name]
        try:
            proc = subprocess.Popen(
                args, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            output = proc.communicate(lines.encode())[0]
            output = output.decode()
        except FileNotFoundError:
            print(
                "Error: yapf not found in PATH. Is it installed?",
                file=sys.stderr)
            return (lines, False, False)

        if lines == output:
            return (lines, False, True)
        else:
            return (output, True, True)
