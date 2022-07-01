"""This task removes extra newlines after the line containing "class"."""

import regex

from wpiformat.task import Task


class JavaClass(Task):
    @staticmethod
    def should_process_file(config_file, name):
        return name.endswith(".java")

    def run_pipeline(self, config_file, name, lines):
        linesep = super().get_linesep(lines)

        output = ""
        pos = 0

        # Match two or more line separators
        token_str = (
            r"/\*|\*/|//|"
            + linesep
            + r"|{"
            + linesep
            + r"(?P<extra>("
            + linesep
            + r")+)"
        )
        token_regex = regex.compile(token_str)

        in_multicomment = False
        in_comment = False

        for match in token_regex.finditer(lines):
            token = match.group()

            if token == "/*":
                in_multicomment = True
            elif token == "*/":
                in_multicomment = False
                in_comment = False
            elif token == "//":
                in_comment = True
            elif token == linesep:
                in_comment = False
            elif not in_multicomment and not in_comment:
                # Otherwise, the token is a class

                # Removes extra line separators
                output += lines[pos : match.span("extra")[0]]
                pos = match.span()[1]

        # Write rest of file if it wasn't all processed
        if pos < len(lines):
            output += lines[pos:]

        return output, True
