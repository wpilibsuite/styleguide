"""This class is for handling wpiformat config files."""

import os
import re


class Config:
    # Dict from filepath to file contents
    __config_cache: dict[str, list[str]] = {}

    def __init__(self, directory: str, filename: str):
        """Constructor for Config object.

        Keyword arguments:
        directory -- directory in which to start search for file
        filename -- filename
        """
        self.__config_dict = self.__parse_config_file(directory, filename)
        self.__c_header_include_regex = self.regex("cHeaderFileInclude")
        self.__cpp_header_include_regex = self.regex("cppHeaderFileInclude")
        self.__cpp_src_include_regex = self.regex("cppSrcFileInclude")
        self.__generated_exclude_regex = self.regex("generatedFileExclude")
        self.__modifiable_exclude_regex = self.regex("modifiableFileExclude")

    @staticmethod
    def read_file(directory: str, filename: str) -> tuple[str, list[str]]:
        """Find file and return contents.

        Checks current directory for file. If one doesn't exist, try all parent
        directories as well.

        Keyword arguments:
        directory -- current directory from which to start search
        filename -- filename

        Returns tuple of filename and list containing file contents or triggers
        program exit.
        """
        while True:
            filepath = os.path.join(directory, filename)
            try:
                # If filepath in config cache, return cached version instead
                if config_file := Config.__config_cache.get(filepath):
                    return filepath, config_file

                with open(filepath, "r") as file_contents:
                    contents = file_contents.read().splitlines()
                    Config.__config_cache[filepath] = contents

                    # TODO: Remove deprecation message
                    if filename.startswith(".styleguide"):
                        print(
                            f"warning: rename deprecated {filepath} to {filepath.replace('styleguide', 'wpiformat')}"
                        )

                    return filepath, contents
            except OSError as e:
                # .git files are ignored, which are created within submodules
                if os.path.isdir(directory + os.sep + ".git"):
                    raise OSError(
                        f"config file '{filename}' not found in '{directory}'"
                    ) from e
                directory = os.path.dirname(directory)

    def group(self, group_name: str) -> list[str]:
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

    def regex(self, *args) -> re.Pattern:
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
            return re.compile(r"a^")
        else:
            return re.compile(r"|".join(group_contents))

    def is_c_file(self, filename: str) -> bool:
        """Returns True if file is either C header or C source file.

        Keyword arguments:
        filename -- filename
        """
        return self.is_c_header_file(filename) or self.is_c_src_file(filename)

    def is_c_header_file(self, filename: str) -> bool:
        """Returns True if file is C header file.

        Keyword arguments:
        filename -- filename
        """
        return self.__c_header_include_regex.search(filename) is not None

    @staticmethod
    def is_c_src_file(filename: str) -> bool:
        """Returns True if file is C source file.

        Keyword arguments:
        filename -- filename
        """
        return filename.endswith(".c")

    def is_cpp_file(self, filename: str) -> bool:
        """Returns True if file is either C++ header or C++ source file.

        Keyword arguments:
        filename -- filename
        """
        return self.is_cpp_header_file(filename) or self.is_cpp_src_file(filename)

    def is_cpp_header_file(self, filename: str) -> bool:
        """Returns True if file is C++ header file.

        Keyword arguments:
        filename -- filename
        """
        return self.__cpp_header_include_regex.search(filename) is not None

    def is_cpp_src_file(self, filename: str) -> bool:
        """Returns True if file is C++ source file.

        Keyword arguments:
        filename -- filename
        """
        return self.__cpp_src_include_regex.search(filename) is not None

    def is_header_file(self, filename: str) -> bool:
        """Returns True if file is either C or C++ header file.

        Keyword arguments:
        filename -- filename
        """
        return self.is_c_header_file(filename) or self.is_cpp_header_file(filename)

    def is_generated_file(self, filename: str) -> bool:
        """Returns True if file is generated (generated files are skipped).

        Keyword arguments:
        filename -- filename
        """
        return self.__generated_exclude_regex.search(filename) is not None

    def is_modifiable_file(self, filename: str) -> bool:
        """Returns True if file is modifiable but should be skipped.

        Keyword arguments:
        filename -- filename
        """
        return self.__modifiable_exclude_regex.search(filename) is not None

    def __parse_config_file(
        self, directory: str, filename: str
    ) -> dict[str, list[str]]:
        """Parse values from config file.

        Checks current directory for config file. If one doesn't exist, try all
        parent directories as well.

        Keyword arguments:
        directory -- current directory from which to start search
        filename -- config filename

        Returns dictionary of groups (group name -> list of values).
        """
        in_group = False
        config_group = {}
        group_name = ""
        group_elements = []

        self.filename, lines = self.read_file(directory, filename)
        if not lines:
            return {}

        for line in lines:
            # Skip empty lines
            if line.strip() == "":
                continue

            if "{" in line:
                in_group = True

                # Group name is on same line as "{"
                group_name = line[: line.find("{")].strip()
            elif "}" in line:
                in_group = False

                # After group closes, save element list and clear it
                config_group[group_name] = group_elements
                group_elements = []
            elif in_group:
                value = line.strip()

                # Header includes still use forward slash on Windows
                unescaped_groups = [
                    "includeRelated",
                    "includeCSys",
                    "includeCppSys",
                    "includeOtherLibs",
                    "includeProject",
                ]
                if group_name == "includeGuardRoots":
                    # Include guard roots use native directory separators
                    value = value.replace("/", os.sep)
                elif group_name not in unescaped_groups and os.sep == "\\":
                    # Replace "/" with escaped "\" for regexes on Windows
                    value = value.replace("/", os.sep + os.sep)

                group_elements.append(value)
        return config_group
