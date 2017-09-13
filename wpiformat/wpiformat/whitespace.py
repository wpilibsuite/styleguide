"""This task removes trailing whitespace from the file."""

import os

from wpiformat.task import Task


class Whitespace(Task):

    def run_pipeline(self, config_file, name, lines):
        linesep = Task.get_linesep(lines)

        file_changed = False
        output = ""

        for line in lines.splitlines():
            processed_line = line[0:len(line)].rstrip()
            if not file_changed and len(line) != len(processed_line):
                file_changed = True
            output += processed_line + linesep

        return (output, file_changed, True)
