"""This task ensures the trailing comment on the closing brace of extern and
namespace declarations matches that of the declaration name.
"""

import re

from wpiformat.task import Task


class BraceComment(Task):

    def should_process_file(self, config_file, name):
        return config_file.is_c_file(name) or config_file.is_cpp_file(name)

    def run_pipeline(self, config_file, name, lines):
        linesep = Task.get_linesep(lines)
        output = ""

        brace_prefix = "(?P<prefix>(extern|namespace)\s+[\w\"]*)"
        brace_postfix = "\s*/(/|\*)[^\r\n]*"

        brace_regex = re.compile(
            "(" + brace_prefix + "\s*)?{|"  # "{" with optional prefix
            "\}(" + brace_postfix + ")?")  # "}" with optional comment postfix

        name_stack = []
        brace_count = 0
        extract_location = 0
        for match in re.finditer(brace_regex, lines):
            token = match.group(0)

            if match.group("prefix"):
                brace_count += 1
                name_stack.append((brace_count, match.group("prefix").rstrip()))
            elif "{" in token:
                brace_count += 1
            elif token.startswith("}"):
                output += lines[extract_location:match.start()]
                if len(name_stack) > 0 and name_stack[len(name_stack) -
                                                      1][0] == brace_count:
                    output += "}  // " + name_stack.pop()[1]
                else:
                    output += lines[match.start():match.end()]
                extract_location = match.end()
                brace_count -= 1

        # If input has unprocessed lines, write them to output
        if extract_location < len(lines):
            output += lines[extract_location:]

        if output != lines:
            return (output, True, True)
        else:
            return (lines, False, True)
