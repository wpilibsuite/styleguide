"""This task disallows "using" declarations in global namespaces in headers."""

import re

from . import task


class Namespace(task.Task):

    def get_file_extensions(self):
        return task.get_config("cppHeaderExtensions")

    def run(self, name, lines):
        linesep = task.get_linesep(lines)
        format_succeeded = True

        # Tokenize file as brace opens, brace closes, and "using" declarations.
        # "using" declarations are scoped, so content inside any bracket pair
        # is considered outside the global namespace.
        regex_str = "(\{|\}|using .*;)"

        brace_count = 0
        for match in re.finditer(regex_str, lines):
            token = match.group(0)

            if token == "{":
                brace_count += 1
            elif token == "}":
                brace_count -= 1
            elif token.startswith("using"):
                if brace_count == 0:
                    linenum = lines.count(linesep, 0, match.start()) + 1
                    if "NOLINT" not in lines.splitlines()[linenum - 1]:
                        format_succeeded = False
                        print(name + ": " + str(linenum) + ": '" + token + \
                              "' in global namespace")

        return (lines, False, format_succeeded)
