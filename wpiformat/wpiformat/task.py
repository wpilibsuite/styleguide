"""Provides a task base class for use by format.py.

format.py excludes matches for the "modifiable" regex before checking for
modifications to generated files because some of the regexes from each group
overlap.
"""

from abc import *
import os


class Task:
    __metaclass__ = ABCMeta

    @staticmethod
    def get_linesep(lines):
        """Returns string containing autodetected line separator for file.

        Keyword arguments:
        lines -- file contents string
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

    @staticmethod
    def get_repo_root():
        """Returns the Git repository root as an absolute path.

        An empty string is returned if no repository root was found.
        """
        current_dir = os.path.abspath(os.getcwd())
        while current_dir != os.path.dirname(current_dir):
            if os.path.exists(current_dir + os.sep + ".git"):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        return ""

    @abstractmethod
    def should_process_file(self, config_file, name):
        """Returns true if file should be processed by this task.

        Keyword arguments:
        config_file -- Config object
        name -- file name string

        Process any file by default.
        """
        return True

    @abstractmethod
    def run_pipeline(self, config_file, name, lines):
        """Performs task on file with given lines.

        This function is for processing the file in a pipeline of tasks.

        Keyword arguments:
        config_file -- Config object
        name -- file name string
        lines -- file contents string

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
        config_file -- Config object
        names -- list of file name strings

        Returns True if task succeeded in formatting the files.
        """
        return True
