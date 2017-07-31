"""This task runs clang-format on the file."""

import subprocess
import sys

from . import task


class ClangFormat(task.Task):

    def should_process_file(self, name):
        extensions = task.get_config("cExtensions") + \
            task.get_config("cppHeaderExtensions") + \
            task.get_config("cppSrcExtensions")

        return any(name.endswith("." + ext) for ext in extensions)

    def run_all(self, names):
        args = ["-style=file", "-i"] + names
        try:
            returncode = subprocess.call(["clang-format-3.9"] + args)
        except FileNotFoundError:
            try:
                returncode = subprocess.call(["clang-format"] + args)
            except FileNotFoundError:
                print(
                    "Error: clang-format not found in PATH. Is it installed?",
                    file=sys.stderr)
                return False
        return returncode == 0
