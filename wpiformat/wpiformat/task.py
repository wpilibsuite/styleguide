"""Task base classes for wpiformat."""

from abc import ABCMeta, abstractmethod
import subprocess


class Task(metaclass=ABCMeta):
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
        return subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            encoding="ascii",
        ).stdout.rstrip()

    @staticmethod
    def should_process_file(config_file, name):
        """Returns true if file should be processed by this task.

        Keyword arguments:
        config_file -- Config object
        name -- file name string

        Process any file by default.
        """
        return True


class PipelineTask(Task):
    @abstractmethod
    def run_pipeline(self, config_file, name, lines):
        """Performs task on file with given lines.

        This function is for processing the file in a pipeline of tasks.

        Keyword arguments:
        config_file -- Config object
        name -- file name string
        lines -- file contents string

        Returns tuple containing processed lines and whether task succeeded in
        processing the file.
        """
        return ("", True)


class BatchTask(Task):
    @staticmethod
    @abstractmethod
    def run_batch(config_file, names):
        """Performs task on list of files.

        This function is for processing multiple files in one task to reduce
        overhead.

        Keyword arguments:
        config_file -- Config object
        names -- list of file name strings

        Returns True if task succeeded in processing the files.
        """
        return True


class StandaloneTask(Task):
    @abstractmethod
    def run_standalone(self, config_file, name):
        """Performs task on a file.

        This function is for processing the file on its own.

        Keyword arguments:
        config_file -- Config object
        name -- file name string

        Returns True if task succeeded in processing the file.
        """
        return True
