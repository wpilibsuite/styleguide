"""This task runs black on files with Python extension."""

import subprocess
import sys

from wpiformat.config import Config
from wpiformat.task import BatchTask


class PyFormat(BatchTask):
    @staticmethod
    def should_process_file(config_file: Config, filename: str) -> bool:
        return filename.endswith(".py")

    @staticmethod
    def run_batch(config_file: Config, filenames: list[str]) -> bool:
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
            subprocess.run(args + filenames)
        except FileNotFoundError:
            print(
                "error: autoflake not found in PATH. Is it installed?", file=sys.stderr
            )
            return False

        try:
            args = [sys.executable, "-m", "black", "-q"]
            subprocess.run(args + filenames)
        except FileNotFoundError:
            print("error: black not found in PATH. Is it installed?", file=sys.stderr)
            return False

        try:
            args = [sys.executable, "-m", "isort", "--profile", "black", "-q"]
            subprocess.run(args + filenames)
        except FileNotFoundError:
            print("error: isort not found in PATH. Is it installed?", file=sys.stderr)
            return False

        return True
