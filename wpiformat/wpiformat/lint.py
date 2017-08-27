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

    def __init__(self, repo_root):
        task.Task.__init__(self)

        self.repo_root = repo_root

    def should_process_file(self, config_file, name):
        return config_file.is_cpp_file(name)

    def run_all(self, config_file, names):
        # Handle running in either the root or styleguide directories
        cpplintPrefix = ""
        if os.getcwd().rpartition(os.sep)[2] != "styleguide":
            cpplintPrefix = "styleguide/"

        # Prepare arguments to cpplint.py
        saved_argv = sys.argv
        sys.argv = ["cpplint.py",
                    "--extensions=" + \
                        ",".join(config_file.group("cppHeaderExtensions") + \
                                 config_file.group("cppSrcExtensions")),
                    "--headers=" + \
                        ",".join(config_file.group("cppHeaderExtensions")),
                    "--repository=" + self.repo_root,
                    "--includeroots=" + \
                        ",".join(config_file.group("includeGuardRoots"))] + \
                   names

        # Run cpplint.py
        try:
            cpplint.main()
        except SystemExit as e:
            # Restore original arguments
            sys.argv = saved_argv

            # Report success if error code is 0 (False)
            return e.code == False
