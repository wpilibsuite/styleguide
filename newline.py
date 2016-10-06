"""This task ensures that the file has exactly one EOF newline."""

from task import Task

class Newline(Task):
    def run(self, name, lines):
        linesep = Task.get_linesep(lines)

        newlines = 0

        # Handle trivial case
        if len(lines) == 0:
            return (linesep, True, True)

        pos = len(lines) - 1

        # While last character is a newline
        while lines[pos] == "\n":
            newlines += 1

            # Seek to character before newline
            pos = pos - len(linesep)

        if newlines < 1:
            # Append newline to end of file
            return (lines + linesep, True, True)
        elif newlines > 1:
            # Truncate all but one newline
            return (lines[0:len(lines) - len(linesep) * (newlines - 1)], True,
                    True)
        else:
            return (lines, False, True)
