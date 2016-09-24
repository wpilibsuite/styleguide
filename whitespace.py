"""This task removes trailing whitespace from the file."""

import os

from task import Task

class Whitespace(Task):
    def run(self, name, lines):
        file_changed = False
        output = ""

        eol = os.linesep
        if name.endswith("bat"):
            eol = "\r\n"

        for line in lines.splitlines():
            processed_line = line[0:len(line)].rstrip()
            if not file_changed and len(line) != len(processed_line):
                file_changed = True
            output += processed_line + eol

        return (output, file_changed)
