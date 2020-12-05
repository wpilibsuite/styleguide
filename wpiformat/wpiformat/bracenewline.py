"""This task ensures braces are followed by two line separators."""

import re

from wpiformat.task import Task


class BraceNewline(Task):

    def should_process_file(self, config_file, name):
        return config_file.is_c_file(name) or config_file.is_cpp_file(
            name) or name.endswith("java")

    def run_pipeline(self, config_file, name, lines):
        linesep = Task.get_linesep(lines)

        comment_regex = re.compile("//|/\*|\*/")

        lines_list = lines.split(linesep)

        in_multiline_comment = False
        for i in range(len(lines_list)):
            match = comment_regex.search(lines_list[i])
            if not match:
                line = lines_list[i].rstrip()
            else:
                # While in a multiline comment, we only care about "*/"
                if in_multiline_comment:
                    if match.group() == "*/":
                        line = lines_list[i][match.start() +
                                             len("*/"):].rstrip()
                        in_multiline_comment = False
                else:
                    line = lines_list[i][0:match.start()].rstrip()

                    # If multiline comment is starting
                    if match.group() == "/*":
                        line = lines_list[i][0:match.start()]
                        in_multiline_comment = True

                        # If comment ends on same line, handle it immediately
                        comment_end = lines_list[i].find("*/")
                        if comment_end != -1:
                            line += lines_list[i][comment_end + len("*/"):]
                            line = line.rstrip()
                            in_multiline_comment = False

            if in_multiline_comment:
                continue

            # If line with "}" isn't at end of file
            if i + 1 < len(lines_list) and line.endswith("}"):
                next_line = lines_list[i + 1].lstrip()

                # If next line is already empty, there's nothing to do
                if len(next_line) > 0:
                    if next_line[
                            0] != "}" and "else" not in next_line and "#endif" not in next_line:
                        lines_list.insert(i + 1, "")
                        i += 1

        return (linesep.join(lines_list), True)
