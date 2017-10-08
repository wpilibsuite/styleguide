"""This task updates the license header at the top of the file."""

import os
import re
import sys

from wpiformat.config import Config
from wpiformat.task import Task


class LicenseUpdate(Task):

    def __init__(self, current_year):
        """Constructor for LicenseUpdate task.

        Keyword arguments:
        current_year -- year string
        """
        Task.__init__(self)

        self.__current_year = current_year

    def should_process_file(self, config_file, name):
        license_regex = config_file.regex("licenseUpdateExclude")

        return (config_file.is_c_file(name) or config_file.is_cpp_file(name) or
                name.endswith(".java")) and not license_regex.search(name)

    def run_pipeline(self, config_file, name, lines):
        linesep = Task.get_linesep(lines)

        license_template = Config.read_file(
            os.path.dirname(os.path.abspath(name)), ".styleguide-license")

        # Strip newlines at top of file
        stripped_lines = lines.lstrip().split(linesep)

        # If a comment at the beginning of the file is considered a license, it
        # is replaced with an updated license. Otherwise, a license header is
        # inserted before it.
        first_comment_is_license = False
        license_end = 0

        # Regex for tokenizing on comment boundaries
        regex_str = "(^/\*|\*/|^//)"

        in_multiline_comment = False
        for line in stripped_lines:
            # If part of comment contains "Copyright (c)", comment is license.
            if "Copyright (c)" in line:
                first_comment_is_license = True

            line_has_comment = False
            for match in re.finditer(regex_str, line):
                # If any comment token was matched, the line has a comment
                line_has_comment = True

                token = match.group(0)

                if token == "/*":
                    in_multiline_comment = True
                elif token == "*/":
                    in_multiline_comment = False
            if not in_multiline_comment and not line_has_comment:
                break
            else:
                license_end += 1

        # If comment at beginning of file is non-empty license, update it
        if first_comment_is_license and license_end > 0:
            file_parts = \
                [linesep.join(stripped_lines[0:license_end]),
                 linesep + linesep.join(stripped_lines[license_end:]).lstrip()]
        else:
            file_parts = ["", linesep + lines.lstrip()]

        # Default year when none is found is current one
        year = self.__current_year

        year_regex = re.compile("Copyright \(c\).*\s(20..)")
        modify_copyright = False
        for line in file_parts[0].split(linesep):
            match = year_regex.search(line)
            # If license contains copyright pattern, extract the first year
            if match:
                year = match.group(1)
                modify_copyright = True
                break

        output = ""

        # Determine copyright range and trailing padding
        if modify_copyright and year != self.__current_year:
            year = year + "-" + self.__current_year

        for line in license_template:
            # Insert copyright year range
            line = line.replace("{year}", year)

            # Insert padding which expands to the 80th column. If there is more
            # than one padding token, the line may contain fewer than 80
            # characters due to rounding during the padding width calculation.
            PADDING_TOKEN = "{padding}"
            padding_count = line.count(PADDING_TOKEN)
            if padding_count:
                padding = 80 - len(line) + len(PADDING_TOKEN) * padding_count
                padding_width = int(padding / padding_count)
                line = line.replace(PADDING_TOKEN, " " * padding_width)

            output += line + linesep

        # Copy rest of original file into new one
        if len(file_parts) > 1:
            output += file_parts[1]

        return (output, lines != output, True)
