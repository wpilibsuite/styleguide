"""Provides a task base class for use by format.py.

format.py excludes matches for the "modifiable" regex before checking for
modifications to generated files because some of the regexes from each group
overlap.
"""

from abc import *
import os
import re
import subprocess
import sys


def read_file(file_name):
    """Find file and return contents.

    Checks current directory for file. If one doesn't exist, try all parent
    directories as well.

    file_name -- name of file

    Returns list containing file contents or None if file was not found.
    """
    file_found = False
    directory = os.getcwd()
    while not file_found and len(directory) > 0:
        try:
            with open(directory + os.sep + file_name, "r") as file_contents:
                file_found = True
                return file_contents.read().splitlines()
        except OSError:
            directory = directory[:directory.rfind(os.sep)]
    return None


def parse_config_file(file_name):
    """Parse values from config file.

    Checks current directory for config file. If one doesn't exist, try all
    parent directories as well.

    file_name -- name of config file

    Returns dictionary of groups (group name -> list of values).
    """
    in_group = False
    config_groups = {}
    group_name = ""
    group_elements = []

    lines = read_file(file_name)
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
            config_groups[group_name] = group_elements
            group_elements = []
        elif in_group:
            value = line.strip()

            # header includes still use forward slash on Windows
            nonescaped_groups = [
                "includeRelated", "includeCSys", "includeCppSys",
                "includeOtherLibs", "includeProject"
            ]
            if group_name not in nonescaped_groups and os.sep == "\\":
                # On Windows, replace "/" with escaped "\" for regexes
                value = value.replace("/", os.sep + os.sep)

            group_elements.extend([value])
    return config_groups


config_dict = parse_config_file(".styleguide")
if not config_dict:
    print("Error: config file '.styleguide' not found")
    sys.exit(1)


def get_config(key_name):
    """Returns value from config dictionary given key string.
    """
    try:
        return config_dict[key_name]
    except KeyError:
        return []


def group_to_regex(*args):
    """Converts contents of groups from config file into properly escaped regex.

    Keyword arguments:
    *args -- argument list of groups. They are all joined by "|".
    """
    group_contents = []

    for group in args:
        group = get_config(group)

        # If group exists
        if len(group) > 0:
            group_contents.extend(group)

    if len(group_contents) == 0:
        # If regex string is empty, make regex match nothing
        return "a^"
    else:
        regex_str = "|".join(group_contents)
    return regex_str


# Regex for generated file exclusions
gen_exclude_regex = re.compile(group_to_regex("genFileExclude"))

# Regex for modifiable file exclusions
modifiable_exclude_regex = re.compile(group_to_regex("modifiableFileExclude"))


def is_modifiable_file(name):
    """Returns True if file is modifiable but should not have tasks run on it.
    """
    return modifiable_exclude_regex.search(name)


def is_generated_file(name):
    """Returns True if file isn't generated (generated files are skipped).
    """
    return gen_exclude_regex.search(name)


def filter_ignored_files(names):
    """Returns list of files not in .gitignore.
    """
    cmd = ["git", "check-ignore", "--no-index", "-n", "-v", "--stdin"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    # "git check-ignore" misbehaves when the names are separated by "\r\n" on
    # Windows, so os.linesep isn't used here.
    output = proc.communicate("\n".join(names).encode())[0]

    # "git check-ignore" prefixes the names of non-ignored files with "::",
    # wraps names in quotes on Windows, and outputs "\n" line separators on all
    # platforms.
    return [
        name[2:].lstrip().strip("\"").replace("\\\\", "\\")
        for name in output.decode().split("\n") if name[0:2] == "::"
    ]


def get_linesep(lines):
    """Returns autodetected line separator for file.
    """
    # Find potential line separator
    pos = lines.find("\n")

    # If a newline character was found and the character preceding it is a
    # carriage return, assume CRLF line endings. LF line endings are assumed
    # for empty files.
    if pos > 0 and lines[pos - 1] == "\r":
        return "\r\n"
    else:
        return "\n"


class Task(object):
    __metaclass__ = ABCMeta

    def should_process_file(self, name):
        """Returns True if file should be processed by this task.

        Match anything by default.
        """
        return [".*"]

    @abstractmethod
    def run(self, name, lines):
        """Performs task on file with given lines.

        Keyword arguments:
        name -- file name string
        lines -- file contents

        Returns tuple containing processed lines, whether lines were changed,
        and whether task succeeded in formatting the file.
        """
        return ("", False, True)

    @abstractmethod
    def run_all(self, names):
        """Performs task on list of files.

        Keyword arguments:
        names -- list of file name strings

        Returns True if task succeeded in formatting the files.
        """
        return True
