"""This class is for handling wpiformat config files."""

import os
import regex
import sys


class Config:

    def __init__(self, directory, file_name):
        """Constructor for Config object.

        Keyword arguments:
        directory -- directory in which to start search for file
        file_name -- file name string
        """
        self.__config_dict = self.__parse_config_file(directory, file_name)
        self.__c_header_include_regex = self.regex("cHeaderFileInclude")
        self.__cpp_header_include_regex = self.regex("cppHeaderFileInclude")
        self.__cpp_src_include_regex = self.regex("cppSrcFileInclude")
        self.__generated_exclude_regex = self.regex("generatedFileExclude")
        self.__modifiable_exclude_regex = self.regex("modifiableFileExclude")

    @staticmethod
    def read_file(directory, file_name):
        """Find file and return contents.

        Checks current directory for file. If one doesn't exist, try all parent
        directories as well.

        Keyword arguments:
        directory -- current directory from which to start search
        file_name -- file name string

        Returns list containing file contents or triggers program exit.
        """
        file_found = False
        while not file_found:
            try:
                with open(directory + os.sep + file_name, "r") as file_contents:
                    file_found = True
                    return file_contents.read().splitlines()
            except OSError:
                # .git files are ignored, which are created within submodules
                if os.path.isdir(directory + os.sep + ".git"):
                    print("Error: config file '" + file_name + "' not found")
                    sys.exit(1)
                directory = os.path.dirname(directory)

    def group(self, group_name):
        """Returns value from config dictionary given key string.

        Keyword arguments:
        group_name -- config group name
        """
        if not self.__config_dict:
            return []

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
            return regex.compile("a^")
        else:
            return regex.compile("|".join(group_contents))

    def is_c_file(self, name):
        """Returns True if file is either C header or C source file.

        Keyword arguments:
        name -- file name string
        """
        return self.is_c_header_file(name) or self.is_c_src_file(name)

    def is_c_header_file(self, name):
        """Returns True if file is C header file.

        Keyword arguments:
        name -- file name string
        """
        return self.__c_header_include_regex.search(name) != None

    def is_c_src_file(self, name):
        """Returns True if file is C source file.

        Keyword arguments:
        name -- file name string
        """
        return name.endswith(".c")

    def is_cpp_file(self, name):
        """Returns True if file is either C++ header or C++ source file.

        Keyword arguments:
        name -- file name string
        """
        return self.is_cpp_header_file(name) or self.is_cpp_src_file(name)

    def is_cpp_header_file(self, name):
        """Returns True if file is C++ header file.

        Keyword arguments:
        name -- file name string
        """
        return self.__cpp_header_include_regex.search(name) != None

    def is_cpp_src_file(self, name):
        """Returns True if file is C++ source file.

        Keyword arguments:
        name -- file name string
        """
        return self.__cpp_src_include_regex.search(name) != None

    def is_header_file(self, name):
        """Returns True if file is either C or C++ header file.

        Keyword arguments:
        name -- file name string
        """
        return self.is_c_header_file(name) or self.is_cpp_header_file(name)

    def is_generated_file(self, name):
        """Returns True if file is generated (generated files are skipped).

        Keyword arguments:
        name -- file name string
        """
        return self.__generated_exclude_regex.search(name) != None

    def is_modifiable_file(self, name):
        """Returns True if file is modifiable but should be skipped.

        Keyword arguments:
        name -- file name string
        """
        return self.__modifiable_exclude_regex.search(name) != None

    def __parse_config_file(self, directory, file_name):
        """Parse values from config file.

        Checks current directory for config file. If one doesn't exist, try all
        parent directories as well.

        Keyword arguments:
        directory -- current directory from which to start search
        file_name -- config file name string

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

                # Header includes still use forward slash on Windows
                unescaped_groups = [
                    "includeRelated", "includeCSys", "includeCppSys",
                    "includeOtherLibs", "includeProject"
                ]
                if group_name == "includeGuardRoots":
                    # Include guard roots use native directory separators
                    value = value.replace("/", os.sep)
                elif group_name not in unescaped_groups and os.sep == "\\":
                    # Replace "/" with escaped "\" for regexes on Windows
                    value = value.replace("/", os.sep + os.sep)

                group_elements.append(value)
        return config_group
