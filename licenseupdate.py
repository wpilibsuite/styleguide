"""This task updates the license header at the top of the file."""

from datetime import date
from functools import partial
import hashlib
import os
import re
import sys

from task import Task

class LicenseUpdate(Task):
    def get_file_extensions(self):
        return Task.get_config("cExtensions") + \
            Task.get_config("cppHeaderExtensions") + \
            Task.get_config("cppSrcExtensions") + \
            Task.get_config("otherExtensions")

    def run(self, name):
        license_template = \
            self.read_license_template(".styleguide-license", name)
        if not license_template:
              print("Error: license template file '.styleguide-license' not " \
                    "found")
              sys.exit(1)

        lines = []
        with open(name, "r") as file:
            lines = file.read()

        # License should be at beginning of file and followed by two newlines.
        # If a comment exists at the top of the file, treat it as the license
        # header
        if lines.startswith("//") or lines.startswith("/*"):
            file_parts = lines.split("\n\n", 1)
        else:
            file_parts = ["", lines.lstrip()]

        year_regex = re.compile("Copyright \(c\) [\w\s]+\s+(20..)")
        year = ""
        modify_copyright = False
        for line in file_parts[0].split("\n"):
            match = year_regex.search(line)
            # If license contains copyright pattern, extract the first year
            if match:
                year = match.group(1)
                modify_copyright = True
                break

        with open(name + ".tmp", "w") as temp:
            # Determine copyright range and trailing padding
            current_year = str(date.today().year)
            if modify_copyright and year != current_year:
                current_year = year + "-" + current_year

            for line in license_template:
                # Insert copyright year range
                line = line.replace("{year}", current_year)

                # Insert padding which expands to the 80th column. If there is
                # more than one padding token, the line may contain fewer than
                # 80 characters due to rounding during the padding width
                # calculation.
                PADDING_TOKEN = "{padding}"
                padding_count = line.count(PADDING_TOKEN)
                if padding_count:
                    padding = 80 - len(line) + len(PADDING_TOKEN) * \
                        padding_count
                    padding_width = int(padding / padding_count)
                    line = line.replace(PADDING_TOKEN, " " * padding_width)

                temp.write(line + "\n")

            # Copy rest of original file into new one
            temp.write("\n")
            temp.write(file_parts[1])

        # Replace old file if it was changed
        if self.md5sum(name) != self.md5sum(name + ".tmp"):
            os.remove(name)
            os.rename(name + ".tmp", name)
        else:
            os.remove(name + ".tmp")

    """Read license template from file

    Checks current directory for config file. If one doesn't exist, try all
    parent directories as well.

    template_name -- name of license template file
    file_name -- name of file currently being processed

    Returns list containing license template or None if file was not found.
    """
    @staticmethod
    def read_license_template(template_name, file_name):
        config_found = False
        directory = os.path.dirname(file_name)
        while not config_found and len(directory) > 0:
            try:
                template_location = directory + os.sep + template_name
                with open(template_location, "r") as template_file:
                    config_found = True
                    return template_file.read().splitlines()
            except OSError:
                directory = directory[:directory.rfind(os.sep)]
        return None

    # Compute MD5 sum of file
    @staticmethod
    def md5sum(name):
        with open(name, mode = "rb") as file:
            digest = hashlib.md5()
            for buf in iter(partial(file.read, 128), b""):
                digest.update(buf)
        return digest.hexdigest()
