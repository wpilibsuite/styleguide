"""This task runs cpplint.py on all C++ source files.

The `update-cpplint.py` script downloads the latest cpplint.py and edits it for
use by lint.py.

cpplint.py was originally spawned as a subprocess whose output was filtered.
When it was moved into a separate repository, the difference in directories
required it to be used as a module.
"""

import os
import sys

import cpplint

from task import Task

class Lint(Task):
    def get_file_extensions(self):
        return Task.get_config("cppHeaderExtensions") + \
            Task.get_config("cppSrcExtensions")

    def run(self, name, lines):
        # Handle running in either the root or styleguide directories
        cpplintPrefix = ""
        if os.getcwd().rpartition(os.sep)[2] != "styleguide":
            cpplintPrefix = "styleguide/"

        # Prepare arguments to cpplint.py
        saved_argv = sys.argv
        sys.argv = ["cpplint.py", "--filter="
                    "-build/c++11,"
                    "-build/include,"
                    "-build/include_subdir,"
                    "-build/namespaces,"
                    "-readability/todo,"
                    "-runtime/references,"
                    "-runtime/string",
                    "--extensions=" + \
                        ",".join(self.get_config("cppHeaderExtensions") + \
                                 self.get_config("cppSrcExtensions")),
                    "--headers=" + \
                        ",".join(Task.get_config("cppHeaderExtensions")),
                    "--quiet",
                    name]

        # Run cpplint.py
        try:
            cpplint.main()
        except SystemExit:
            pass

        # Restore original arguments
        sys.argv = saved_argv
