"""This task ensures the trailing comment on the closing brace of extern and
namespace declarations matches that of the declaration name.
"""

import regex

from wpiformat.task import PipelineTask


class BraceComment(PipelineTask):
    @staticmethod
    def should_process_file(config_file, name):
        return config_file.is_c_file(name) or config_file.is_cpp_file(name)

    def run_pipeline(self, config_file, name, lines):
        linesep = super().get_linesep(lines)
        output = ""

        brace_prefix = r"(?P<prefix>(extern|namespace)\s+[\w\"]*)"
        brace_postfix = r"[ \t]*/(/|\*)[^\r\n]*"

        brace_regex = regex.compile(
            r"/\*|\*/|//|\\\\|\\\"|\"|\\'|'|"
            + linesep
            + r"|"
            + r"("
            + brace_prefix
            + r"\s*)?{|"  # "{" with optional prefix
            r"}(" + brace_postfix + r")?"
        )  # "}" with optional comment postfix

        name_stack = []
        brace_count = 0
        extract_location = 0
        in_multicomment = False
        in_singlecomment = False
        in_string = False
        in_char = False
        for match in brace_regex.finditer(lines):
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
            elif match.group("prefix"):
                brace_count += 1
                name_stack.append((brace_count, match.group("prefix").rstrip()))
            elif "{" in token:
                brace_count += 1
            elif token.startswith("}"):
                output += lines[extract_location : match.start()]
                if (
                    len(name_stack) > 0
                    and name_stack[len(name_stack) - 1][0] == brace_count
                ):
                    output += "}  // " + name_stack.pop()[1]
                else:
                    output += lines[match.start() : match.end()]
                extract_location = match.end()
                brace_count -= 1

        # If input has unprocessed lines, write them to output
        if extract_location < len(lines):
            output += lines[extract_location:]

        return output, True
