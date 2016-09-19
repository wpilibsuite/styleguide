# WPILib Style Guide

This repository contains our style guides for C++ and Java code, various IDE support files, and formatting scripts.

- [Description](#description)
- [Contributing to Style Guide](#contributing-to-style-guide)

## Description

Anything submitted to a wpilibsuite project needs to follow the code style guides outlined here. For details about the style, please see the contributors document [here](CONTRIBUTING.md#coding-guidelines).

## Setup

### Dependencies

- [Python 3.5](https://www.python.org/downloads/)
- clang-format 3.8 or newer (included with [LLVM](http://llvm.org/releases/download.html))

After cloning this repository, set the `WPI_FORMAT` environment variable to its location. If you would like to use these tools with a new project, copy [formatw.py](formatw.py), [.styleguide](#.styleguide), and [.styleguide-license](#.styleguide-license) into the project.

### .styleguide

`format.py` checks the current directory for the `.styleguide` file. If one doesn't exist, all parent directories are tried as well. [.styleguide](.styleguide) is an example with all possible groups.

This file contains groups of file name regular expressions. There are two groups of regexes which prevent tasks (i.e., formatters and linters) from running on matching files:

- generated files
- modifiable files

Generated files should not be modified; if they are, `format.py` will emit warnings.

Config groups may be empty, but may not be omitted. Directory separators must be "/", not "\". During processing, they will be replaced internally with an os.sep that is automatically escaped for regexes.

The groups `includeRelated`, `includeCSys`, `includeCppSys`, `includeOtherLibs`, and `includeProject` correspond to the header groups in the style guide. If a header name matches a regex in one of the groups, it overrides the default ordering and is placed in the corresponding group. The groups of regexes are checked in order of include group precedence.

### .styleguide-license

This file contains the license header template. It should contain `Copyright (c)` followed by the company name and the string `{year}`. [.styleguide-license](.styleguide-license) is an example.

`format.py` checks the currently processed file's directory for a `.styleguide` file first and traverses up the directory tree if one isn't found. This allows templates which are closer to the processed file to override a project's main template.

The license header is always at the beginning of the file and ends after two
newlines. If there isn't one, or it doesn't contain the required copyright
contents, format.py inserts a new one containing the current year.

`{year}` is replaced with a year range from the earliest copyright year in the
file to the current year. If the earliest year is the current year, only that
year will be written.

`{padding}` is optional and represents an expanding space which pads the line to
80 columns. Multiple instances of `{padding}` on the same line share the padding
equally.

## Contributing to Style Guide

See [CONTRIBUTING.md](CONTRIBUTING.md).
