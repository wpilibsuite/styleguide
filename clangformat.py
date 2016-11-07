"""This task runs clang-format on the file."""

import subprocess
import sys

import task


class ClangFormat(task.Task):

    def get_file_extensions(self):
        return task.get_config("cExtensions") + \
            task.get_config("cppHeaderExtensions") + \
            task.get_config("cppSrcExtensions")

    def run_all(self, names):
        args = ["-style=file", "-i"] + names
        try:
            returncode = subprocess.call(["clang-format-3.8"] + args)
        except FileNotFoundError:
            try:
                returncode = subprocess.call(["clang-format"] + args)
            except FileNotFoundError:
                print(
                    "Error: clang-format not found in PATH. Is it installed?",
                    file=sys.stderr)
                return False
        return returncode == 0
