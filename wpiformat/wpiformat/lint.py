"""This task runs cpplint.py on a C++ source file.

The `update-cpplint.py` script downloads the latest cpplint.py and edits it for
use by lint.py.

cpplint.py was originally spawned as a subprocess whose output was filtered.
When it was moved into a separate repository, the difference in directories
required it to be used as a module.
"""

import os
import sys

from wpiformat import cpplint
from wpiformat.task import Task


class Lint(Task):

    def should_process_file(self, config_file, name):
        return config_file.is_cpp_file(name)

    def run_batch(self, config_file, names):
        # Handle running in either the root or styleguide directories
        cpplintPrefix = ""
        if os.getcwd().rpartition(os.sep)[2] != "styleguide":
            cpplintPrefix = "styleguide/"

        # Prepare arguments to cpplint.py
        saved_argv = sys.argv

        # Prepare source file and header file regex strings
        srcs = config_file.group("cppSrcFileInclude")
        if srcs:
            srcs = "|".join(srcs)
        else:
            srcs = "a^"
        headers = config_file.group("cHeaderFileInclude") + \
                  config_file.group("cppHeaderFileInclude")
        if headers:
            headers = "|".join(headers)
        else:
            headers = "a^"

        sys.argv = ["cpplint.py",
                    "--srcs=" + srcs,
                    "--headers=" + headers] + \
                   names

        # Run cpplint.py
        try:
            cpplint.main()
        except SystemExit as e:
            # Restore original arguments
            sys.argv = saved_argv

            # Report success if error code is 0 (False)
            return e.code == False
