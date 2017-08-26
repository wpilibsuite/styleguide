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

    def should_process_file(self, config_file, name):
        extensions = config_file.group("cExtensions") + \
            config_file.group("cppHeaderExtensions") + \
            config_file.group("cppSrcExtensions")

        return any(name.endswith("." + ext) for ext in extensions)

    def run_all(self, config_file, names):
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
