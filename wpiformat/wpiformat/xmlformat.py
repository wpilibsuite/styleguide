"""This task runs tidy on XML files."""

import os
import subprocess
import sys

from wpiformat.config import Config
from wpiformat.task import Task
from wpiformat.whitespace import Whitespace


class XmlFormat(Task):

    def should_process_file(self, config_file, name):
        return name.endswith(".xml")

    def run_batch(self, config_file, names):
        try:
            tidy_config = Config.find_file(os.getcwd(), "tidy-xml.conf")
            if not tidy_config:
                return False
            args = [
                "tidy", "-xml", "-config", tidy_config, "-modify", "-q",
                "--tidy-mark", "false"
            ]
            returncode = subprocess.call(args + names)
        except FileNotFoundError:
            print("Error: tidy not found in PATH. Is it installed?",
                  file=sys.stderr)
            return False

        # Run Whitespace task on files
        for name in names:
            lines = ""
            with open(name, "r") as file:
                try:
                    lines = file.read()
                except UnicodeDecodeError:
                    print("Error: " + name +
                          " contains characters not in UTF-8. "
                          "Should this be considered a generated file?")
                    return False
            output, file_changed, success = Whitespace().run_pipeline(
                config_file, name, lines)
            if file_changed:
                with open(name, "wb") as file:
                    file.write(output.encode())
        return True
