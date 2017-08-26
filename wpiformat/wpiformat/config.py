"""This class is for handling wpiformat config files."""

import os
import re
import sys


class Config:

    def __init__(self, directory, file_name):
        self.__config_dict = self.__parse_config_file(directory, file_name)
        self.__generated_exclude_regex = self.regex("genFileExclude")
        self.__modifiable_exclude_regex = self.regex("modifiableFileExclude")

    @staticmethod
    def read_file(directory, file_name):
        """Find file and return contents.

        Checks current directory for file. If one doesn't exist, try all parent
        directories as well.

        directory -- current directory from which to start search
        file_name -- name of file

        Returns list containing file contents or triggers program exit.
        """
        file_found = False
        while not file_found:
            try:
                with open(directory + os.sep + file_name, "r") as file_contents:
                    file_found = True
                    return file_contents.read().splitlines()
            except OSError:
                if os.path.exists(directory + os.sep + ".git"):
                    print("Error: config file '" + file_name + "' not found")
                    sys.exit(1)
                directory = os.path.dirname(directory)

    def group(self, group_name):
        """Returns value from config dictionary given key string."""
        try:
            return self.__config_dict[group_name]
        except KeyError:
            return []

    def regex(self, *args):
        """Converts contents of group from config file into regex.

        Keyword arguments:
        *args -- argument list of groups. They are all joined by "|".

        Returns compiled regex.
        """
        group_contents = []

        for group_name in args:
            group = self.group(group_name)

            # If group exists
            if len(group) > 0:
                group_contents.extend(group)

        if len(group_contents) == 0:
            # If regex string is empty, make regex match nothing
            return re.compile("a^")
        else:
            return re.compile("|".join(group_contents))

    def is_generated_file(self, name):
        """Returns True if file isn't generated (generated files are skipped).
        """
        return self.__generated_exclude_regex.search(name)

    def is_modifiable_file(self, name):
        """Returns True if file is modifiable but should not have tasks run on it.
        """
        return self.__modifiable_exclude_regex.search(name)

    def __parse_config_file(self, directory, file_name):
        """Parse values from config file.

        Checks current directory for config file. If one doesn't exist, try all
        parent directories as well.

        directory -- current directory from which to start search
        file_name -- name of config file

        Returns dictionary of groups (group name -> list of values).
        """
        in_group = False
        config_group = {}
        group_name = ""
        group_elements = []

        lines = self.read_file(directory, file_name)
        if not lines:
            return None

        for line in lines:
            # Skip empty lines
            if line.strip() == "":
                continue

            if "{" in line:
                in_group = True

                # Group name is on same line as "{"
                group_name = line[:line.find("{")].strip()
            elif "}" in line:
                in_group = False

                # After group closes, save element list and clear it
                config_group[group_name] = group_elements
                group_elements = []
            elif in_group:
                value = line.strip()

                # header includes still use forward slash on Windows
                unescaped_groups = [
                    "includeRelated", "includeCSys", "includeCppSys",
                    "includeOtherLibs", "includeProject"
                ]
                if group_name not in unescaped_groups and os.sep == "\\":
                    # On Windows, replace "/" with escaped "\" for regexes
                    value = value.replace("/", os.sep + os.sep)

                group_elements.append(value)
        return config_group
