"""This task removes trailing whitespace from the file."""

import os

from wpiformat.task import Task


class Whitespace(Task):

    def run_pipeline(self, config_file, name, lines):
        linesep = super().get_linesep(lines)

        output = ""

        for line in lines.splitlines():
            processed_line = line[0:len(line)].rstrip()
            output += processed_line + linesep

        return output, True
