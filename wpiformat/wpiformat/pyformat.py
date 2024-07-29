"""This task runs black on files with Python extension."""

import subprocess
import sys

from wpiformat.task import BatchTask


class PyFormat(BatchTask):
    @staticmethod
    def should_process_file(config_file, name):
        return name.endswith(".py")

    @staticmethod
    def run_batch(config_file, names):
        try:
            args = [
                sys.executable,
                "-m",
                "autoflake",
                "--remove-all-unused-imports",
                "--remove-unused-variables",
                "--ignore-init-module-imports",
                "--quiet",
                "-i",
            ]
            subprocess.run(args + names)
        except FileNotFoundError:
            print(
                "Error: autoflake not found in PATH. Is it installed?", file=sys.stderr
            )
            return False

        try:
            args = [sys.executable, "-m", "black", "-q"]
            subprocess.run(args + names)
        except FileNotFoundError:
            print("Error: black not found in PATH. Is it installed?", file=sys.stderr)
            return False

        return True
