"""This task runs yapf on files with Python extension."""

import subprocess
import sys

import task


class PyFormat(task.Task):

    def get_file_extensions(self):
        return ["py"]

    def run_all(self, names):
        try:
            returncode = \
                subprocess.call(["yapf", "--style", "google", "-i"] + names)
        except FileNotFoundError:
            print(
                "Error: yapf not found in PATH. Is it installed?",
                file=sys.stderr)
            return False
        return True
