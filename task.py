"""Provides a task base class for use by format.py"""

from abc import *
import os
import re
import sys

regexSep = os.sep
# If directory separator is backslash, escape it for regexes
if regexSep == "\\":
    regexSep += "\\"

# There are two groups of regexes which prevent tasks from running on matching
# files:
#   1) generated files (shouldn't be modified)
#   2) modifiable files
#
# format.py excludes matches for the "modifiable" regex before checking for
# modifications to generated files because some of the regexes from each group
# overlap.

"""Read values from config file

Checks current directory for config file. If one doesn't exist, try all parent
directories as well.

A config file takes the form:

```
cExtensions {
  c
}

cppExtensions {
  cpp
  h
  inc
}

otherExtensions {
  java
}

genFolderExclude {
  folder1
  folder2/subdir1/subdir2
}

genFileExclude {
  header1\.h$
  header2\.h$
}

modifiableFolderExclude {
  \.git
  __pycache__
  folder/subdir
}

modifiableFileExclude {
  \.jar$
  \.patch$
}
```

Directory separators must be "/", not "\". During processing, they will be
replaced internally with an os.sep that is automatically escaped for regexes.

Returns dictionary of groups (group name -> list of values).
"""
def readConfigFile(configName):
    configFound = False
    directory = os.getcwd()
    while not configFound and len(directory) > 0:
        try:
            with open(directory + os.sep + configName, "r") as configFile:
                configFound = True

                inGroup = False
                configGroups = {}
                groupName = ""
                groupElements = []

                for line in configFile:
                    # Skip empty lines
                    if line.strip() == "":
                        continue

                    if "{" in line:
                        inGroup = True

                        # Group name is on same line as "{"
                        groupName = line[:line.find("{")].strip()
                    elif "}" in line:
                        inGroup = False

                        # After group closes, save element list and clear it
                        configGroups[groupName] = groupElements
                        groupElements = []
                    elif inGroup:
                        value = line.strip()

                        # On Windows, replace "/" with escaped "\" for regexes
                        if os.sep == "\\":
                            value = value.replace("/", regexSep)

                        groupElements.extend([value])
                return configGroups
        except OSError:
            directory = directory[:directory.rfind(os.sep)]

configDict = readConfigFile(".styleguide")
if not configDict:
    print("Error: config file \".styleguide\" not found")
    sys.exit(1)

# List of regexes for folders which contain generated files
genFolderExclude = [name + regexSep for name in configDict["genFolderExclude"]]

# List of regexes for generated files
genFileExclude = configDict["genFileExclude"]

# Regex for generated file exclusions
genExclude = genFolderExclude + genFileExclude
if len(genExclude) == 0:
    # If there are no file exclusions, make regex match nothing
    genRegexExclude = re.compile("a^")
else:
    genRegexExclude = re.compile("|".join(genExclude))

# Regex for folders which contain modifiable files
modifiableFolderExclude = \
    [name + regexSep for name in configDict["modifiableFolderExclude"]]

# List of regexes for modifiable files
modifiableFileExclude = configDict["modifiableFileExclude"]

# Regex for modifiable file exclusions
modifiableExclude = modifiableFolderExclude + modifiableFileExclude
if len(modifiableExclude) == 0:
    # If there are no file exclusions, make regex match nothing
    modifiableRegexExclude = re.compile("a^")
else:
    modifiableRegexExclude = re.compile("|".join(modifiableExclude))

class Task(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.regexInclude = re.compile("|".join(["\." + ext + "$" for ext in
                                                 self.getIncludeExtensions()]))

    # Extensions of files which should be included in processing
    def getIncludeExtensions(self):
        return []

    # Perform task on file with given name
    @abstractmethod
    def run(self, name):
        return

    # Returns value from config dictionary given key string
    @staticmethod
    def getConfig(keyName):
        return configDict[keyName]

    # Returns True if file is modifiable but should not have tasks run on it
    @staticmethod
    def isModifiableFile(name):
        return modifiableRegexExclude.search(name)

    # Returns True if file isn't generated (generated files are skipped)
    @staticmethod
    def isGeneratedFile(name):
        return genRegexExclude.search(name)

    # Returns True if file has an extension this task can process
    def fileMatchesExtension(self, name):
        if self.getIncludeExtensions() != []:
            return self.regexInclude.search(name)
        else:
            return True
