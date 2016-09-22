"""This task runs clang-format on the file."""

import subprocess
import sys

from task import Task

class ClangFormat(Task):
    def get_file_extensions(self):
        return Task.get_config("cExtensions") + \
            Task.get_config("cppHeaderExtensions") + \
            Task.get_config("cppSrcExtensions")

    def run(self, name):
        # Run clang-format
        if subprocess.call(["clang-format", "-i", "-style=file", name]) == -1:
            print("Error: clang-format not found in PATH. Is it installed?",
                  file = sys.stderr)
