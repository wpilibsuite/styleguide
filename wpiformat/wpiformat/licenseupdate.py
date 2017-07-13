"""This task updates the license header at the top of the file."""

import os
import re
import sys

from . import task


class LicenseUpdate(task.Task):

    def __init__(self, current_year):
        task.Task.__init__(self)

        self.current_year = current_year

    def should_process_file(self, name):
        extensions = task.get_config("cExtensions") + \
            task.get_config("cppHeaderExtensions") + \
            task.get_config("cppSrcExtensions") + \
            task.get_config("otherExtensions")

        return not task.skip_licenseupdate(name) and \
            any(name.endswith("." + ext) for ext in extensions)

    def run(self, name, lines):
        linesep = task.get_linesep(lines)

        license_template = task.read_file(".styleguide-license")
        if not license_template:
            print("Error: license template file '.styleguide-license' not " \
                  "found")
            sys.exit(1)

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
        year = self.current_year

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
        if modify_copyright and year != self.current_year:
            year = year + "-" + self.current_year

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
