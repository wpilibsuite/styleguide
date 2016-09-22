"""This task ensures that the file has exactly one EOF newline."""

import os

from task import Task

class Newline(Task):
    def run(self, name, lines):
        newlines = 0

        eol = os.linesep
        if name.endswith("bat"):
            eol = "\r\n"

        # Handle trivial case
        if len(lines) == 0:
            return (eol, True)

        pos = len(lines) - 1

        # While last character is a newline
        while lines[pos] == "\n":
            newlines += 1

            # Seek to character before newline
            pos = pos - len(eol)

        if newlines < 1:
            # Append newline to end of file
            return (lines + eol, True)
        elif newlines > 1:
            # Truncate all but one newline
            return (lines[0:len(lines) - len(eol) * (newlines - 1)], True)
        else:
            return (lines, False)
