"""This task runs clang-format on the file."""

import subprocess
import sys

from . import task


class ClangFormat(task.Task):

    def __init__(self, clang_version):
        task.Task.__init__(self)

        if clang_version == "":
            self.exec_name = "clang-format"
        else:
            self.exec_name = "clang-format-" + clang_version

    def should_process_file(self, name):
        extensions = task.get_config("cExtensions") + \
            task.get_config("cppHeaderExtensions") + \
            task.get_config("cppSrcExtensions")

        return any(name.endswith("." + ext) for ext in extensions)

    def run_all(self, names):
        args = ["-style=file", "-i"] + names
        try:
            returncode = subprocess.call([self.exec_name] + args)
        except FileNotFoundError:
            print(
                "Error: " + self.exec_name +
                " not found in PATH. Is it installed?",
                file=sys.stderr)
            return False
        return returncode == 0
