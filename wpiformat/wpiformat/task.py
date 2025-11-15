"""Task base classes for wpiformat."""

import os
import subprocess
from abc import ABCMeta, abstractmethod

from wpiformat.config import Config


class Task(metaclass=ABCMeta):
    @staticmethod
    def get_linesep(lines: str) -> str:
        """Returns string containing autodetected line separator for file.

        Keyword arguments:
        lines -- file contents
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
    def get_repo_root() -> str:
        """Returns the Git repository root as an absolute path.

        An empty string is returned if no repository root was found.
        """
        return os.path.normpath(
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"], encoding="ascii"
            ).rstrip()
        )

    @staticmethod
    def should_process_file(config_file: Config, filename: str) -> bool:
        """Returns true if file should be processed by this task.

        Keyword arguments:
        config_file -- Config object
        name -- filename

        Process any file by default.
        """
        return True


class PipelineTask(Task):
    @abstractmethod
    def run_pipeline(
        self, config_file: Config, filename: str, lines: str
    ) -> tuple[str, bool]:
        """Performs task on file with given lines.

        This function is for processing the file in a pipeline of tasks.

        Keyword arguments:
        config_file -- Config object
        name -- filename
        lines -- file contents

        Returns tuple containing processed lines and whether task succeeded in
        processing the file.
        """
        return "", True


class BatchTask(Task):
    @staticmethod
    @abstractmethod
    def run_batch(config_file: Config, filenames: list[str]) -> bool:
        """Performs task on list of files.

        This function is for processing multiple files in one task to reduce
        overhead.

        Keyword arguments:
        config_file -- Config object
        filenames -- list of filenames

        Returns True if task succeeded in processing the files.
        """
        return True


class StandaloneTask(Task):
    @abstractmethod
    def run_standalone(self, config_file: Config, filename: str) -> bool:
        """Performs task on a file.

        This function is for processing the file on its own.

        Keyword arguments:
        config_file -- Config object
        filename -- filename

        Returns True if task succeeded in processing the file.
        """
        return True
