wpiformat
#########

Provides linters and formatters for ensuring WPILib's C++, Java, and Python code conform to its style guide. WPILib uses a variant of the Google style guides.

Setup
*****

Dependencies
============

- `Python 3.4 or newer <https://www.python.org/downloads/>`_
- clang-format 3.8 or newer (included with `LLVM <http://llvm.org/releases/download.html>`_)

If you would like to use these tools with a new project, copy `.styleguide`_, and `.styleguide-license`_ into the project.

Installation
============

On Windows, execute::

    py -m pip install wpiformat

On Linux/OSX, execute::

    pip install wpiformat

.styleguide
-----------

wpiformat checks the current directory for the ``.styleguide`` file. If one doesn't exist, all parent directories are tried as well. See the ``.styleguide`` file in the docs/examples directory for all possible groups.

This file contains groups of file name regular expressions. There are two groups of regexes which prevent tasks (i.e., formatters and linters) from running on matching files:

- generated files
- modifiable files

Generated files should not be modified; if they are, wpiformat will emit warnings. No warnings are emitted for modifications to modifiable files. All files ignored by patterns in a repository's .gitignore file are considered modifiable files.

File names matching regexes in the group ``licenseUpdateExclude`` will be skipped by the license header update task.

Empty config groups can be omitted. Directory separators must be "/", not "\". During processing, they will be replaced internally with an os.sep that is automatically escaped for regexes.

The groups ``includeRelated``, ``includeCSys``, ``includeCppSys``, ``includeOtherLibs``, and ``includeProject`` correspond to the header groups in the style guide. If a header name matches a regex in one of the groups, it overrides the default ordering and is placed in the corresponding group. The groups of regexes are checked in order of include group precedence.

.styleguide-license
-------------------

This file contains the license header template. It should contain ``Copyright (c)`` followed by the company name and the string ``{year}``. See the ``.styleguide-license`` file in the docs/examples directory.

wpiformat checks the currently processed file's directory for a ``.styleguide`` file first and traverses up the directory tree if one isn't found. This allows templates which are closer to the processed file to override a project's main template.

The license header is always at the beginning of the file and ends after two newlines. If there isn't one, or it doesn't contain the required copyright contents, wpiformat inserts a new one containing the current year.

``{year}`` is replaced with a year range from the earliest copyright year in the file to the current year. If the earliest year is the current year, only that year will be written.

``{padding}`` is optional and represents an expanding space which pads the line to 80 columns. Multiple instances of ``{padding}`` on the same line share the padding equally.
