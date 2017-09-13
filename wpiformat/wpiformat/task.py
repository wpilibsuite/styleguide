"""Provides a task base class for use by format.py.

format.py excludes matches for the "modifiable" regex before checking for
modifications to generated files because some of the regexes from each group
overlap.
"""

from abc import *


class Task(object):
    __metaclass__ = ABCMeta

    @staticmethod
    def get_linesep(lines):
        """Returns autodetected line separator for file.
        """
        # Find potential line separator
        pos = lines.find("\n")

        # If a newline character was found and the character preceding it is a
        # carriage return, assume CRLF line endings. LF line endings are assumed
        # for empty files.
        if pos > 0 and lines[pos - 1] == "\r":
            return "\r\n"
        else:
            return "\n"

    @abstractmethod
    def should_process_file(self, config_file, name):
        """Returns True if file should be processed by this task.

        Match anything by default.
        """
        return [".*"]

    @abstractmethod
    def run_pipeline(self, config_file, name, lines):
        """Performs task on file with given lines.

        This function is for processing the file in a pipeline of tasks.

        Keyword arguments:
        name -- file name string
        lines -- file contents

        Returns tuple containing processed lines, whether lines were changed,
        and whether task succeeded in formatting the file.
        """
        return ("", False, True)

    @abstractmethod
    def run_batch(self, config_file, names):
        """Performs task on list of files.

        This function is for processing multiple files in one task to reduce
        overhead.

        Keyword arguments:
        names -- list of file name strings

        Returns True if task succeeded in formatting the files.
        """
        return True
