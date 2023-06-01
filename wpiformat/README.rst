wpiformat
#########

Provides linters and formatters for ensuring WPILib's C++, Java, and Python code conform to its style guide. WPILib uses a variant of the Google style guides.

Dependencies
************

- `Python 3.6 or newer <https://www.python.org/downloads/>`_

Installation
************

On Windows, execute::

    py -m pip install wpiformat

On Linux/OSX, execute::

    pip install wpiformat

Project Setup
*************

To use these tools with a new project, copy `.styleguide`_, and `.styleguide-license`_ from the examples folder into the project and create a new ``.clang-format`` file based on the desired C/C++ style.

Note: Since wpiformat already handles include ordering, it is recommended to use ``SortIncludes: false`` in ``.clang-format``.

.styleguide
-----------

wpiformat checks the current directory for the ``.styleguide`` file. If one doesn't exist, all parent directories are tried as well. See the ``.styleguide`` file in the docs/examples directory for all possible groups.

This file contains groups of file name regular expressions. There are two groups of regexes which prevent tasks (i.e., formatters and linters) from running on matching files:

- generated files
- modifiable files

Generated files should not be modified; if they are, wpiformat will emit warnings. No warnings are emitted for modifications to modifiable files. All files ignored by patterns in a repository's .gitignore file are considered modifiable files. Exclusion groups take precedence over inclusion groups.

File names matching regexes in the group ``licenseUpdateExclude`` will be skipped by the license header update task.

Empty config groups can be omitted. Directory separators must be "/", not "\\". During processing, they will be replaced internally with an os.sep that is automatically escaped for regexes.

Valid include guard patterns use capital letters, start with the repository name, include the path to the file and the file name itself, have directory separators and hyphens replaced with underscores, and have a trailing underscore. The path to the file starts from the repository root by default. Other paths, such as include directories, can be specified in the group ``includeGuardRoots``. If a path matches, that string will be truncated from the include guard pattern.

For example, given a file at `allwpilib/src/main/native/include/wpiutil/support/ConcurrentQueue.h` and an include path of `src/main/native/include/`, the resulting include guard would be `ALLWPILIB_WPIUTIL_SUPPORT_CONCURRENTQUEUE_H_`.

The group ``repoRootNameOverride`` allows one to override the repository name used in include guards. This is useful for giving subprojects within one repository different repository roots in their include guards. Only specify one name in this group because subsequent names will be ignored.

The groups ``includeRelated``, ``includeCSys``, ``includeCppSys``, ``includeOtherLibs``, and ``includeProject`` correspond to the header groups in the style guide. If a header name matches a regex in one of the groups, it overrides the default ordering and is placed in the corresponding group. The groups of regexes are checked in order of include group precedence.

The regex for C system headers produces false positives on headers from "other libraries". Regexes for them should be added to ``includeOtherLibs``. Libraries with many headers generally group them within a folder, so a regex for just the folder will suffice.

``NOLINT`` can be appended in a comment to a header include to prevent wpiformat's header include sorter from modifying it and to maintain its relative ordering with other header includes. This will, in effect, treat it as a barrier across which no header includes will be moved. Header includes on each side of the barrier will still be sorted as normal.

.styleguide-license
-------------------

This file contains the license header template. It should contain ``Copyright (c)`` followed by the company name and the string ``{year}``. See the ``.styleguide-license`` file in the docs/examples directory.

wpiformat checks the currently processed file's directory for a ``.styleguide`` file first and traverses up the directory tree if one isn't found. This allows templates which are closer to the processed file to override a project's main template.

The license header is always at the beginning of the file and ends after two newlines. If there isn't one, or it doesn't contain the required copyright contents, wpiformat inserts a new one containing the current year.

``{year}`` is replaced with a year range from the earliest copyright year in the file to the current year. If the earliest year is the current year, only that year will be written.

``{padding}`` is optional and represents an expanding space which pads the line to 80 columns. Multiple instances of ``{padding}`` on the same line share the padding equally.
