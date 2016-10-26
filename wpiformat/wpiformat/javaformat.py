"""This task runs google-java-format.jar on the file."""

import subprocess
import sys

from wpiformat.task import Task


class JavaFormat(Task):

    def should_process_file(self, config_file, name):
        return name.endswith(".java")

    def run_batch(self, config_file, names):
        try:
            formatter_name = "google-java-format-1.5-all-deps.jar"
            args = ["java", "-jar", formatter_name, "--replace"]
            returncode = subprocess.call(args + names)
        except FileNotFoundError:
            print("Error: " + formatter_name +
                  " not found in PATH. Is it installed?",
                  file=sys.stderr)
            return False
        return True
