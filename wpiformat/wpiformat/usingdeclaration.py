"""This task disallows "using" declarations in global namespaces in headers."""

import regex

from wpiformat.task import Task


class UsingDeclaration(Task):

    def should_process_file(self, config_file, name):
        return config_file.is_cpp_header_file(name)

    def run_pipeline(self, config_file, name, lines):
        linesep = Task.get_linesep(lines)
        format_succeeded = True

        # Tokenize file as brace opens, brace closes, and "using" declarations.
        # "using" declarations are scoped, so content inside any bracket pair is
        # considered outside the global namespace.
        token_regex = regex.compile(
            "/\*|\*/|//|" + linesep + "|\{|\}|using\s[^;]*;")

        brace_count = 0
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
