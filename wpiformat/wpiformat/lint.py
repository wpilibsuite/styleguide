"""This task runs cpplint.py on a C++ source file.

The `update-cpplint.py` script downloads the latest cpplint.py and edits it for
use by lint.py.

cpplint.py was originally spawned as a subprocess whose output was filtered.
When it was moved into a separate repository, the difference in directories
required it to be used as a module.
"""

import os
import sys

from . import cpplint
from . import task


class Lint(task.Task):

    def get_file_extensions(self):
        return task.get_config("cppHeaderExtensions") + \
            task.get_config("cppSrcExtensions")

    def run_all(self, names):
        # Handle running in either the root or styleguide directories
        cpplintPrefix = ""
        if os.getcwd().rpartition(os.sep)[2] != "styleguide":
            cpplintPrefix = "styleguide/"

        # Prepare arguments to cpplint.py
        saved_argv = sys.argv
        sys.argv = ["cpplint.py", "--filter="
                    "-build/c++11,"
                    "-build/include,"
                    "-build/include_order,"  # includeorder.py handles ordering
                    "-build/include_subdir,"
                    "-build/namespaces,"
                    "-readability/todo,"
                    "-runtime/references,"
                    "-runtime/string,"
                    "-whitespace/indent",  # clangformat.py handles indentation
                    "--extensions=" + \
                        ",".join(task.get_config("cppHeaderExtensions") + \
                                 task.get_config("cppSrcExtensions")),
                    "--headers=" + \
                        ",".join(task.get_config("cppHeaderExtensions")),
                    "--quiet"] + names

        # Run cpplint.py
        try:
            cpplint.main()
        except SystemExit as e:
            # Restore original arguments
            sys.argv = saved_argv

            # Report success if error code is 0 (False)
            return e.code == False
