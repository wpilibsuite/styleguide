"""This task removes trailing whitespace from the file."""

import os

from wpiformat.task import Task


class Whitespace(Task):
    def run_pipeline(self, config_file, name, lines):
        linesep = super().get_linesep(lines)

        return "".join(line.rstrip() + linesep for line in lines.splitlines()), True
