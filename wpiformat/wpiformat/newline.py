"""This task ensures that the file has exactly one EOF newline."""

from wpiformat.task import Task


class Newline(Task):

    def run_pipeline(self, config_file, name, lines):
        output = lines.rstrip() + Task.get_linesep(lines)

        if output != lines:
            return (output, True, True)
        else:
            return (lines, False, True)
