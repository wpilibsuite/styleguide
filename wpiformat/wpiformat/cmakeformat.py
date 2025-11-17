"""This task runs gersemi on CMake files."""

import subprocess
import sys
from pathlib import Path

from wpiformat.config import Config
from wpiformat.task import BatchTask


class CMakeFormat(BatchTask):
    @staticmethod
    def should_process_file(config_file: Config, filename: Path) -> bool:
        return filename.name == "CMakeLists.txt" or filename.suffix == ".cmake"

    @staticmethod
    def run_batch(config_file: Config, filenames: list[Path]) -> bool:
        try:
            args = [sys.executable, "-m", "gersemi", "-i", "--no-color", "-q"]
            subprocess.run(args + [f.as_posix() for f in filenames])
        except FileNotFoundError:
            print("error: gersemi not found in PATH. Is it installed?", file=sys.stderr)
            return False
        return True
