"""This task runs black on files with Python extension."""

import subprocess
import sys

from wpiformat.task import Task


class PyFormat(Task):
    @staticmethod
    def should_process_file(config_file, name):
        return name.endswith(".py")

    @staticmethod
    def run_batch(config_file, names):
        try:
            # Force one worker because wpiformat already uses a process pool,
            # and we need to keep the total number of multiprocessing processes
            # below the Windows system limit.
            args = [sys.executable, "-m", "black", "--workers", "1", "-q"]
            subprocess.run(args + names)
        except FileNotFoundError:
            print("Error: black not found in PATH. Is it installed?", file=sys.stderr)
            return False
        return True
