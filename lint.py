"""This task runs cpplint.py on all C++ source files.

The `update-cpplint.py` script downloads the latest cpplint.py and edits it for
use by lint.py.

cpplint.py was originally spawned as a subprocess whose output was filtered.
When it was moved into a separate repository, the difference in directories
required it to be used as a module. Redirecting stderr is not thread-safe and
overloading print() did not work, so the print statements causing that output
where removed from cpplint.py.
"""

import os
import sys

import cpplint
from task import Task

class Lint(Task):
    def getIncludeExtensions(self):
        return Task.getConfig("cppExtensions")

    def run(self, name):
        # Handle running in either the root or styleguide directories
        cpplintPrefix = ""
        if os.getcwd().rpartition(os.sep)[2] != "styleguide":
            cpplintPrefix = "styleguide/"

        # Prepare arguments to cpplint.py
        savedArgv = sys.argv
        sys.argv = ["cpplint.py", "--filter="
                    "-build/c++11,"
                    "-build/header_guard,"
                    "-build/include,"
                    "-build/namespaces,"
                    "-readability/todo,"
                    "-runtime/references,"
                    "-runtime/string",
                    "--extensions=" + ",".join(self.getIncludeExtensions()),
                    name]

        # Run cpplint.py
        try:
            cpplint.main()
        except SystemExit:
            pass

        # Restore original arguments
        sys.argv = savedArgv
