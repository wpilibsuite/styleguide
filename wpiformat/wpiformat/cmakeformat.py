"""This task runs gersemi on CMake files."""

import subprocess
import sys

from wpiformat.config import Config
from wpiformat.task import BatchTask


class CMakeFormat(BatchTask):
    @staticmethod
    def should_process_file(config_file: Config, filename: str) -> bool:
        return filename.endswith("CMakeLists.txt") or filename.endswith(".cmake")

    @staticmethod
    def run_batch(config_file: Config, filenames: list[str]) -> bool:
        try:
            args = [sys.executable, "-m", "gersemi", "-i", "--no-color", "-q"]
            subprocess.run(args + filenames)
        except FileNotFoundError:
            print("error: gersemi not found in PATH. Is it installed?", file=sys.stderr)
            return False
        return True
