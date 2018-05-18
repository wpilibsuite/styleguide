"""This task runs yapf on files with Python extension."""

import subprocess
import sys

from wpiformat.task import Task


class PyFormat(Task):

    def should_process_file(self, config_file, name):
        return name.endswith(".py")

    def run_batch(self, config_file, names):
        try:
            args = [sys.executable, "-m", "yapf", "--style", "google", "-i"]
            returncode = subprocess.run(args + names).returncode
        except FileNotFoundError:
            print(
                "Error: yapf not found in PATH. Is it installed?",
                file=sys.stderr)
            return False
        return True
