"""This task formats Doxygen and Javadoc comments.

Comments are rewrapped to 80 characters for C++ and 100 for Java. The @param
tag has one space followed by the parameter name, at least one one space, then
the description. All @param descriptions start on the same column.

The first letter of paragraphs and tag descriptions is capitalized and a "." is
appended if one is not already. Descriptions past 80 (or 100) characters are
wrapped to the next line at the same starting column.

The indentation of lists is left alone. Bulleted lists can use "-", "+", or "*"
while numbered lists use numbers followed by ".".
"""

import regex
import sys

from wpiformat.task import Task


class CommentFormat(Task):

    @staticmethod
    def should_process_file(config_file, name):
        return config_file.is_c_file(name) or config_file.is_cpp_file(name) or \
            name.endswith(".java")

    def textwrap(self, lines, column_limit):
        """Wraps lines to the provided column limit and returns a list of lines.

        Keyword Arguments:
        lines -- string to wrap
        column_limit -- maximum number of characters per line
        """
        output = []
        output_str = ""
        pos = 0
        rgx = regex.compile(r"{@link(?>.*?})|\S+")
        for match in rgx.finditer(lines):
            if len(output_str) + len(" ") + len(match.group()) > column_limit:
                output.append(output_str)
                output_str = match.group()
            else:
                if output_str:
                    output_str += " "
                output_str += match.group()
            pos = match.end()
        if output_str:
            output.append(output_str)
        return output

    def run_pipeline(self, config_file, name, lines):
        linesep = Task.get_linesep(lines)

        if name.endswith(".java"):
            column_limit = 100
        else:
            column_limit = 80

        output = ""

        # Construct regex for Doxygen comment
        indent = r"(?P<indent>[ \t]*)?"
        comment_rgx = regex.compile(indent + r"/\*\*(?>(.|" + linesep +
                                    r")*?\*/)")
        asterisk_rgx = regex.compile(r"^\s*(\*|\*/)")

        # Comment parts
        brief = r"(?P<brief>(.|" + linesep + r")*?(" + \
            linesep + linesep + r"|" + linesep + r"$|" + linesep + r"(?=@)|$))"
        brief_rgx = regex.compile(brief)

        tag = r"@(?<tag_name>\w+)\s+(?<arg_name>\w+)\s+(?<description>[^@]*)"
        tag_rgx = regex.compile(tag)

        pos = 0
        for comment_match in comment_rgx.finditer(lines):
            # Append lines before match
            output += lines[pos:comment_match.start()]

            # If there is an indent, create a variable with that amount of
            # spaces in it
            if comment_match.group("indent"):
                spaces = " " * len(comment_match.group("indent"))
            else:
                spaces = ""

            # Append start of comment
            output += spaces + "/**" + linesep

            # Remove comment start/end and leading asterisks from comment lines
            comment = comment_match.group()
            comment = comment[len(comment_match.group("indent")) +
                              len("/**"):len(comment) - len("*/")]
            comment_list = [
                asterisk_rgx.sub("", line).strip()
                for line in comment.split(linesep)
            ]
            comment = linesep.join(comment_list).strip(linesep)

            # Parse comment paragraphs
            comment_pos = 0
            i = 0
            while comment_pos < len(comment) and comment[comment_pos] != "@":
                match = brief_rgx.search(comment[comment_pos:])

                # If no paragraphs were found, bail out early
                if not match:
                    break

                # Start writing paragraph
                if comment_pos > 0:
                    output += spaces + " *" + linesep
                output += spaces + " * "

                # If comments are javadoc and it isn't the first paragraph
                if name.endswith(".java") and comment_pos > 0:
                    if not match.group().startswith("<p>"):
                        # Add paragraph tag before new paragraph
                        output += "<p>"

                # Strip newlines and extra spaces between words from paragraph
                contents = " ".join(match.group().split())

                # Capitalize first letter of paragraph and wrap paragraph
                contents = self.textwrap(
                    contents[:1].upper() + contents[1:],
                    column_limit - len(" * ") - len(spaces))

                # Write out paragraphs
                for i, line in enumerate(contents):
                    if i == 0:
                        output += line
                    else:
                        output += spaces + " * " + line
                    # Put period at end of paragraph
                    if i == len(contents) - 1 and output[-1] != ".":
                        output += "."
                    output += linesep

                comment_pos += match.end()

            # Parse tags
            tag_list = []
            max_arglength = 0
            for match in tag_rgx.finditer(comment[comment_pos:]):
                contents = " ".join(match.group("description").split())
                if match.group("tag_name") == "param":
                    tag_list.append((match.group("tag_name"),
                                     match.group("arg_name"), contents))

                    # Only param tags are lined up and thus count toward the
                    # maximum amount indented
                    max_arglength = max(max_arglength,
                                        len(match.group("arg_name")))
                else:
                    tag_list.append((match.group("tag_name"), "",
                                     match.group("arg_name") + " " + contents))

            # Insert empty line before tags if there was a description before
            if tag_list and comment_pos > 0:
                output += spaces + " *" + linesep

            for tag in tag_list:
                # Only line up param tags
                if tag[0] == "param":
                    tagline = spaces + " * @" + tag[0] + " " + tag[1]
                    tagline += " " * (max_arglength - len(tag[1]) + 1)
                else:
                    tagline = spaces + " * @" + tag[0] + " "

                # Capitalize first letter of description and wrap description
                contents = self.textwrap(
                    tag[2][:1].upper() + tag[2][1:],
                    column_limit - len(tagline) - len(spaces))

                # Write out tags
                output += tagline
                for i, line in enumerate(contents):
                    if i == 0:
                        output += line
                    else:
                        output += spaces + " * " + " " * (
                            len(tagline) - len(spaces) - len(" * ")) + line
                    # Put period at end of description
                    if i == len(contents) - 1 and output[-1] != ".":
                        output += "."
                    output += linesep

            # Append closing part of comment
            output += spaces + " */"
            pos = comment_match.end()

        # Append leftover lines in file
        if pos < len(lines):
            output += lines[pos:]

        if output != lines:
            return (output, True)
        else:
            return (lines, True)
