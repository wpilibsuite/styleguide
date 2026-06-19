"""
This task runs black.

Runs on: Python
"""

import subprocess
import sys
from pathlib import Path

from wpiformat.config import Config
from wpiformat.task import BatchTask


class PyFormat(BatchTask):
    @staticmethod
    def should_process_file(config_file: Config, filename: Path) -> bool:
        return filename.suffix == ".py"

    @staticmethod
    def run_batch(config_file: Config, filenames: list[Path]) -> bool:
        try:
            args = [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--fix",
                "-q",
            ]
            subprocess.run(args + filenames)
        except FileNotFoundError:
            print("error: ruff not found in PATH. Is it installed?", file=sys.stderr)
            return False

        try:
            args = [
                sys.executable,
                "-m",
                "ruff",
                "format",
                "-q",
            ]
            subprocess.run(args + filenames)
        except FileNotFoundError:
            print("error: ruff not found in PATH. Is it installed?", file=sys.stderr)
            return False

        return True
