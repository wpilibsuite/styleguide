"""Provides a task base class for use by format.py."""

from abc import *
import os
import re
import sys

regex_sep = os.sep
# If directory separator is backslash, escape it for regexes
if regex_sep == "\\":
    regex_sep += "\\"

# format.py excludes matches for the "modifiable" regex before checking for
# modifications to generated files because some of the regexes from each group
# overlap.

"""Read values from config file

Checks current directory for config file. If one doesn't exist, try all parent
directories as well.

Returns dictionary of groups (group name -> list of values).
"""
def read_config_file(file_name):
    config_found = False
    directory = os.getcwd()
    while not config_found and len(directory) > 0:
        try:
            with open(directory + os.sep + file_name, "r") as config_file:
                config_found = True

                in_group = False
                config_groups = {}
                group_name = ""
                group_elements = []

                for line in config_file:
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
                        config_groups[group_name] = group_elements
                        group_elements = []
                    elif in_group:
                        value = line.strip()

                        # On Windows, replace "/" with escaped "\" for regexes
                        if os.sep == "\\":
                            value = value.replace("/", regex_sep)

                        group_elements.extend([value])
                return config_groups
        except OSError:
            directory = directory[:directory.rfind(os.sep)]

config_dict = read_config_file(".styleguide")
if not config_dict:
    print("Error: config file '.styleguide' not found")
    sys.exit(1)

# List of regexes for folders which contain generated files
gen_folder_exclude = \
    [name + regex_sep for name in config_dict["genFolderExclude"]]

# List of regexes for generated files
gen_file_exclude = config_dict["genFileExclude"]

# Regex for generated file exclusions
gen_exclude = gen_folder_exclude + gen_file_exclude
if len(gen_exclude) == 0:
    # If there are no file exclusions, make regex match nothing
    gen_regex_exclude = re.compile("a^")
else:
    gen_regex_exclude = re.compile("|".join(gen_exclude))

# Regex for folders which contain modifiable files
modifiable_folder_exclude = \
    [name + regex_sep for name in config_dict["modifiableFolderExclude"]]

# List of regexes for modifiable files
modifiable_file_exclude = config_dict["modifiableFileExclude"]

# Regex for modifiable file exclusions
modifiable_exclude = modifiable_folder_exclude + modifiable_file_exclude
if len(modifiable_exclude) == 0:
    # If there are no file exclusions, make regex match nothing
    modifiable_regex_exclude = re.compile("a^")
else:
    modifiable_regex_exclude = re.compile("|".join(modifiable_exclude))

class Task(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.regex_include = \
            re.compile("|".join(["\." + ext + "$" for ext in
                                 self.get_file_extensions()]))

    # Extensions of files which should be included in processing
    def get_file_extensions(self):
        # Match anything by default
        return [".*"]

    """Performs task on file with given lines.

    Keyword arguments:
    name -- file name string
    lines -- file contents

    Returns tuple containing processed lines, whether lines were changed, and
    whether task succeeded in formatting the file.
    """
    @abstractmethod
    def run(self, name, lines):
        return ("", False, True)

    # Returns value from config dictionary given key string
    @staticmethod
    def get_config(key_name):
        return config_dict[key_name]

    # Returns True if file is modifiable but should not have tasks run on it
    @staticmethod
    def is_modifiable_file(name):
        return modifiable_regex_exclude.search(name)

    # Returns True if file isn't generated (generated files are skipped)
    @staticmethod
    def is_generated_file(name):
        return gen_regex_exclude.search(name)

    # Returns True if file has an extension this task can process
    def file_matches_extension(self, name):
        if self.get_file_extensions() != []:
            return self.regex_include.search(name)
        else:
            return True
