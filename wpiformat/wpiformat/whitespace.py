"""This task removes trailing whitespace from the file."""

import os

from . import task


class Whitespace(task.Task):

    def run(self, name, lines):
        linesep = task.get_linesep(lines)

        file_changed = False
        output = ""

        for line in lines.splitlines():
            processed_line = line[0:len(line)].rstrip()
            if not file_changed and len(line) != len(processed_line):
                file_changed = True
            output += processed_line + linesep

        return (output, file_changed, True)
