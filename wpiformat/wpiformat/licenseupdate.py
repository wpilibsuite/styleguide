"""This task updates the license header at the top of the file."""

from datetime import date
import os
import regex
import subprocess

from wpiformat.config import Config
from wpiformat.task import PipelineTask


class LicenseUpdate(PipelineTask):
    @staticmethod
    def should_process_file(config_file, name):
        license_regex = config_file.regex("licenseUpdateExclude")

        return (
            config_file.is_c_file(name)
            or config_file.is_cpp_file(name)
            or name.endswith(".java")
        ) and not license_regex.search(name)

    def __try_regex(self, lines, last_year, license_template):
        """Try finding license with regex of license template.

        Keyword arguments:
        lines -- lines of file
        last_year -- last year in copyright range
        license_template -- license_template string

        Returns:
        Tuple of whether license was found, first year in copyright range, and
        file contents after license.
        """
        linesep = super().get_linesep(lines)

        # Convert the license template to a regex
        license_rgxstr = "^" + linesep.join(license_template)
        license_rgxstr = (
            license_rgxstr.replace("*", r"\*")
            .replace(".", r"\.")
            .replace("(", r"\(")
            .replace(")", r"\)")
            .replace("{year}", r"(?P<year>[0-9]+)(-[0-9]+)?")
            .replace("{padding}", "[ ]*")
        )
        license_rgx = regex.compile(license_rgxstr, regex.M)

        first_year = last_year

        # Compare license
        match = license_rgx.search(lines)
        if match:
            try:
                first_year = match.group("year")
            except IndexError:
                pass

            # If comment at beginning of file is non-empty license, update it
            return True, first_year, linesep + lines[match.end() :].lstrip()
        else:
            return False, first_year, lines

    def __try_string_search(self, lines, last_year, license_template):
        """Try finding license with string search.

        Keyword arguments:
        lines -- lines of file
        last_year -- last year in copyright range
        license_template -- license_template string

        Returns:
        Tuple of whether license was found, first year in copyright range, and
        file contents after license.
        """
        linesep = super().get_linesep(lines)

        # Strip newlines at top of file
        stripped_lines = lines.lstrip().split(linesep)

        # If a comment at the beginning of the file is considered a license, it
        # is replaced with an updated license. Otherwise, a license header is
        # inserted before it.
        first_comment_is_license = False
        license_end = 0

        # Regex for tokenizing on comment boundaries
        token_regex = regex.compile(r"/\*|\*/|^//")

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

        first_year = last_year

        # If comment at beginning of file is non-empty license, update it
        if first_comment_is_license and license_end > 0:
            license_part = linesep.join(stripped_lines[0:license_end])
            appendix_part = (
                linesep + linesep.join(stripped_lines[license_end:]).lstrip()
            )

            year_regex = regex.compile(r"Copyright \(c\)(?>.*?\s(20..))")
            for line in license_part.split(linesep):
                match = year_regex.search(line)
                # If license contains copyright pattern, extract the first year
                if match:
                    first_year = match.group(1)
                    break

            return True, first_year, appendix_part
        else:
            return False, first_year, linesep + lines.lstrip()

    def run_pipeline(self, config_file, name, lines):
        linesep = super().get_linesep(lines)

        _, license_template = Config.read_file(
            os.path.dirname(os.path.abspath(name)), ".styleguide-license"
        )

        # Get year when file was most recently modified in Git history
        #
        # Committer date is used instead of author date (the one shown by "git
        # log") because the year the file was last modified in the history
        # should be used. Author dates can be older than this or even out of
        # order in the log.
        last_year = subprocess.check_output(
            ["git", "log", "-n", "1", "--format=%ci", "--", name]
        ).decode()[:4]

        # Check if file has uncomitted changes in the working directory
        has_uncommitted_changes = subprocess.run(
            ["git", "diff-index", "--quiet", "HEAD", "--", name]
        ).returncode

        # If file hasn't been committed yet or has changes in the working
        # directory, use current calendar year as end of copyright year range
        if last_year == "" or has_uncommitted_changes:
            last_year = str(date.today().year)

        success, first_year, appendix = self.__try_regex(
            lines, last_year, license_template
        )
        if not success:
            success, first_year, appendix = self.__try_string_search(
                lines, last_year, license_template
            )

        output = ""

        # Determine copyright range and trailing padding
        if first_year != last_year:
            year_range = first_year + "-" + last_year
        else:
            year_range = first_year

        for line in license_template:
            # Insert copyright year range
            line = line.replace("{year}", year_range)

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

        return output, True
