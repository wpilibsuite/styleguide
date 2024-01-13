"""This task disallows "using" declarations in global namespaces in headers."""

import regex

from wpiformat.task import PipelineTask


class UsingDeclaration(PipelineTask):
    @staticmethod
    def should_process_file(config_file, name):
        return config_file.is_cpp_header_file(name)

    def run_pipeline(self, config_file, name, lines):
        linesep = super().get_linesep(lines)
        format_succeeded = True

        # Tokenize file as brace opens, brace closes, and "using" declarations.
        # "using" declarations are scoped, so content inside any bracket pair is
        # considered outside the global namespace.
        token_regex = regex.compile(
            r"/\*|\*/|//|\\\\|\\\"|\"|\\'|'|" + linesep + r"|\{|\}|using\b"
        )

        brace_count = 0
        in_multicomment = False
        in_singlecomment = False
        in_string = False
        in_char = False
        for match in token_regex.finditer(lines):
            token = match.group()

            if token == "/*":
                if not in_singlecomment and not in_string and not in_char:
                    in_multicomment = True
            elif token == "*/":
                if not in_singlecomment and not in_string and not in_char:
                    in_multicomment = False
            elif token == "//":
                if not in_multicomment and not in_string and not in_char:
                    in_singlecomment = True
            elif in_singlecomment and linesep in token:
                # Ignore token if it's in a singleline comment. Only check it
                # for newlines to end the comment.
                in_singlecomment = False
            elif in_multicomment or in_singlecomment:
                # Tokens processed after this branch are ignored if they are in
                # comments
                continue
            elif token == '\\"':
                continue
            elif token == '"':
                if not in_char:
                    in_string = not in_string
            elif token == "\\'":
                continue
            elif token == "'":
                if not in_string:
                    in_char = not in_char
            elif in_string or in_char:
                # Tokens processed after this branch are ignored if they are in
                # double or single quotes
                continue
            elif token == "{":
                brace_count += 1
            elif token == "}":
                brace_count -= 1
            elif token.startswith("using"):
                if brace_count == 0:
                    linenum = lines.count(linesep, 0, match.start()) + 1
                    if "NOLINT" not in lines.splitlines()[linenum - 1]:
                        format_succeeded = False

                        # Extract using declaration
                        using_decl = lines[
                            match.start() : lines.find(";", match.start()) + 1
                        ]

                        print(f"{name}: {linenum}: '{using_decl}' in global namespace")

        return lines, format_succeeded
