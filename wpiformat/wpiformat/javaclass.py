"""This task removes extra newlines after the line containing "class"."""

import re

from wpiformat.task import Task


class JavaClass(Task):

    def should_process_file(self, config_file, name):
        return name.endswith(".java")

    def run_pipeline(self, config_file, name, lines):
        linesep = Task.get_linesep(lines)
        file_changed = False

        if linesep == "\r\n":
            regex_linesep = r"\r\n"
        else:
            regex_linesep = r"\n"

        output = ""
        pos = 0

        # Match two or more line separators
        token_str = "class\s.*{" + regex_linesep + "(?P<extra>(" + regex_linesep + ")+)"
        token_regex = re.compile(token_str, re.MULTILINE)

        for match in token_regex.finditer(lines):
            # Removes extra line separators
            output += lines[pos:match.span("extra")[0]]
            pos = match.span()[1]

            file_changed = True

        # Write rest of file if it wasn't all processed
        if pos < len(lines):
            output += lines[pos:]

        if file_changed:
            return (output, file_changed, True)
        else:
            return (lines, file_changed, True)
