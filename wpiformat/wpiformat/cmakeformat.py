"""This task runs gersemi on CMakeLists.txt files."""

import subprocess
import sys

from wpiformat.task import Task


class CMakeFormat(Task):
    @staticmethod
    def should_process_file(config_file, name):
        return name.endswith("CMakeLists.txt")

    @staticmethod
    def run_batch(config_file, names):
        try:
            args = [sys.executable, "-m", "gersemi", "-l", "150", "-i", "."]
            returncode = subprocess.run(args + names).returncode
        except FileNotFoundError:
            print("Error: gersemi not found in PATH. Is it installed?",
                  file=sys.stderr)
            return False
        return True
