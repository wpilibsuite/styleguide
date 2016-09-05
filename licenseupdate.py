"""This task updates the license comment block at the top of all source files.

If there is already a comment block, a year range through the current year is
created using the first year in the comment. If there is no comment block, a new
one is added containing just the current year.
"""

from datetime import date
from functools import partial
import hashlib
import os

from task import Task

current_year = str(date.today().year)

class LicenseUpdate(Task):
    def get_file_extensions(self):
        return Task.get_config("cExtensions") + \
            Task.get_config("cppExtensions") + \
            Task.get_config("otherExtensions")

    def run(self, name):
        with open(name, "r") as file:
            modify_copyright = False
            year = ""

            # Get first line of file
            line = file.readline()

            # If first line is non-documentation comment
            if line[0:3] == "/*\n" or line[0:3] == "/*-":
                modify_copyright = True

                # Get next line
                line = file.readline()

                # Search for start of copyright year
                pos = line.find("20")

                # Extract it if found. If not, rewrite whole comment
                if pos != -1:
                    year = line[pos:pos + 4]
                else:
                    modify_copyright = False

                # Retrieve lines until one past end of comment block
                in_comment = True
                in_block = True
                while in_block:
                    if not in_comment:
                        pos = line.find("/*", pos)
                        if pos != -1:
                            in_comment = True
                        else:
                            in_block = False
                    else:
                        pos = line.find("*/", pos)
                        if pos != -1:
                            in_comment = False

                        # This assumes no comments are started on the same line
                        # after another ends
                        line = file.readline()
                        pos = 0

            with open(name + ".tmp", "w") as temp:
                # Write first line of comment
                temp.write("/*")
                for i in range(0, 76):
                    temp.write("-")
                temp.write("*/\n")

                # Write second line of comment
                temp.write("/* Copyright (c) FIRST ")
                if modify_copyright and year != current_year:
                    temp.write(year)
                    temp.write("-")
                temp.write(current_year)
                temp.write(". All Rights Reserved.")
                for i in range(0, 24):
                    temp.write(" ")
                if not modify_copyright or year == current_year:
                    for i in range(0, 5):
                        temp.write(" ")
                temp.write("*/\n")

                # Write rest of lines of comment
                temp.write("""\
/* Open Source Software - may be modified and shared by FRC teams. The code   */
/* must be accompanied by the FIRST BSD license file in the root directory of */
/* the project.                                                               */
/*""")
                for i in range(0, 76):
                    temp.write("-")
                temp.write("*/\n")

                # If line after comment block isn't empty
                if len(line) > 1 and line[0] != " ":
                    temp.write("\n")
                temp.write(line)

                # Copy rest of original file into new one
                for line in file:
                    temp.write(line)

        # Replace old file if it was changed
        if self.md5sum(name) != self.md5sum(name + ".tmp"):
            os.remove(name)
            os.rename(name + ".tmp", name)
        else:
            os.remove(name + ".tmp")

    # Compute MD5 sum of file
    @staticmethod
    def md5sum(name):
        with open(name, mode = "rb") as file:
            digest = hashlib.md5()
            for buf in iter(partial(file.read, 128), b""):
                digest.update(buf)
        return digest.hexdigest()
