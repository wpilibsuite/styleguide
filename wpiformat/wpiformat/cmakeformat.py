"""This task runs gersemi on CMake files."""

import subprocess
import sys

from wpiformat.task import BatchTask


class CMakeFormat(BatchTask):
    @staticmethod
    def should_process_file(config_file, name):
        return name.endswith("CMakeLists.txt") or name.endswith(".cmake")

    @staticmethod
    def run_batch(config_file, names):
        try:
            args = [sys.executable, "-m", "gersemi", "-i"]
            subprocess.run(args + names)
        except FileNotFoundError:
            print("Error: gersemi not found in PATH. Is it installed?", file=sys.stderr)
            return False
        return True
