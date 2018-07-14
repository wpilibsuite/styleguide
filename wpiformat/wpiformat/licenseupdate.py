"""This task updates the license header at the top of the file."""

import os
import regex
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

    def __try_regex(self, lines, license_template):
        """Try finding license with regex of license template.

        Keyword arguments:
        lines -- lines of file
        license_template -- license_template string

        Returns:
        Tuple of whether license was found, year, and file contents after license.
        """
        linesep = Task.get_linesep(lines)

        # Convert the license template to a regex
        license_rgxstr = "^" + linesep.join(license_template)
        license_rgxstr = license_rgxstr.replace("*", "\*").replace(
            ".", "\.").replace("(", "\(").replace(")", "\)").replace(
                "{year}", "(?P<year>[0-9]+)(-[0-9]+)?").replace(
                    "{padding}", "[ ]*")
        license_rgx = regex.compile(license_rgxstr, regex.M)

        # Compare license
        year = self.__current_year
        match = license_rgx.search(lines)
        if match:
            try:
                year = match.group("year")
            except IndexError:
                pass

            # If comment at beginning of file is non-empty license, update it
            return (True, year, linesep + lines[match.end():].lstrip())
        else:
            return (False, year, lines)

    def __try_string_search(self, lines, license_template):
        """Try finding license with string search.

        Keyword arguments:
        lines -- lines of file
        license_template -- license_template string

        Returns:
        Tuple of whether license was found, year, and file contents after license.
        """
        linesep = Task.get_linesep(lines)

        # Strip newlines at top of file
        stripped_lines = lines.lstrip().split(linesep)

        # If a comment at the beginning of the file is considered a license, it
        # is replaced with an updated license. Otherwise, a license header is
        # inserted before it.
        first_comment_is_license = False
        license_end = 0

        # Regex for tokenizing on comment boundaries
        token_regex = regex.compile("/\*|\*/|^//")

        in_multiline_comment = False
        for line in stripped_lines:
            # If part of comment contains "Copyright (c)", comment is
            # license.
            if "Copyright (c)" in line:
                first_comment_is_license = True

            line_has_comment = False
            for match in token_regex.finditer(line):
                # If any comment token was matched, the line has a comment
                line_has_comment = True

                token = match.group()

                if token == "/*":
                    in_multiline_comment = True
                elif token == "*/":
                    in_multiline_comment = False
            if not in_multiline_comment and not line_has_comment:
                break
            else:
                license_end += 1

        # If comment at beginning of file is non-empty license, update it
        year = self.__current_year
        if first_comment_is_license and license_end > 0:
            license_part = linesep.join(stripped_lines[0:license_end])
            appendix_part = \
                linesep + linesep.join(stripped_lines[license_end:]).lstrip()

            year_regex = regex.compile("Copyright \(c\)(?>.*?\s(20..))")
            for line in license_part.split(linesep):
                match = year_regex.search(line)
                # If license contains copyright pattern, extract the first year
                if match:
                    year = match.group(1)
                    break

            return (True, year, appendix_part)
        else:
            return (False, year, linesep + lines.lstrip())

    def run_pipeline(self, config_file, name, lines):
        linesep = Task.get_linesep(lines)

        license_template = Config.read_file(
            os.path.dirname(os.path.abspath(name)), ".styleguide-license")

        success, year, appendix = self.__try_regex(lines, license_template)
        if not success:
            success, year, appendix = self.__try_string_search(
                lines, license_template)

        output = ""

        # Determine copyright range and trailing padding
        if year != self.__current_year:
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
        output += appendix

        return (output, lines != output, True)
