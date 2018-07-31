"""This task removes extra newlines after the line containing "class"."""

import regex

from wpiformat.task import Task


class JavaClass(Task):

    def should_process_file(self, config_file, name):
        return name.endswith(".java")

    def run_pipeline(self, config_file, name, lines):
        linesep = Task.get_linesep(lines)
        file_changed = False

        output = ""
        pos = 0

        # Match two or more line separators
        token_str = "/\*|\*/|//|" + linesep + "|class\s[\w\d\s]*{" + linesep + "(?P<extra>(" + linesep + ")+)"
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
