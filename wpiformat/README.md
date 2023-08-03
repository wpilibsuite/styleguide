# wpiformat

Provides linters and formatters for ensuring WPILib's C++, Java, and Python code conform to its style guide. WPILib uses a variant of the Google style guides.

## Dependencies

- [Python 3.9](https://www.python.org/downloads/) or newer

## Installation

On Windows, execute:
```powershell
py -m pip install wpiformat
```

On Linux/OSX, execute:
```bash
pip install wpiformat
```

## Project Setup

To use these tools with a new project, copy `.wpiformat`, and `.wpiformat-license` from the examples folder into the project and create a new `.clang-format` file based on the desired C/C++ style.

Note: Since wpiformat already handles include ordering, it is recommended to use `SortIncludes: false` in `.clang-format`.

## .wpiformat

wpiformat checks the current directory for the `.wpiformat` file. If one doesn't exist, all parent directories are tried as well. This file contains groups of filename regular expressions.
```
groupName {
  regex_here
}
```
The regexes are matched using [re.search()](https://docs.python.org/3/library/re.html#re.search), so they don't have to match the whole filename.

Empty config groups can be omitted. Directory separators must be "/", not "\\". During processing, they will be replaced internally with an os.sep that is automatically escaped for regexes.

See the `.wpiformat` file in the docs/examples directory for all possible groups.

### Specifying C/C++ files to format

The `cHeaderFileInclude` group specifies C headers to format, the `cppHeaderFileInclude` group specifies C++ headers to format, and the `cppSrcFileInclude` group specifies C++ source files to format. It's common to match just the file extension like so: `\.hpp$`.

### Ignoring files

There are two groups of regexes which prevent tasks (i.e., formatters and linters) from running on matching files:

- `generatedFileExclude` (generated files)
- `modifiableFileExclude` (modifiable files)

Generated files should not be modified by the user; if they are, wpiformat will emit warnings. No warnings are emitted for modifications to modifiable files.

All files ignored by patterns in a repository's `.gitignore` file are considered modifiable files. Exclusion groups take precedence over inclusion groups.

### License update exclusion

Filenames matching regexes in the group `licenseUpdateExclude` will be skipped by the license header update task.

### Include guards

Valid include guard patterns have the following properties:

- Use capital letters
- Start with the repository name
- Include the path to the file and the filename itself
- Have directory separators and hyphens replaced with underscores
- Have a trailing underscore

The path to the file starts from the repository root by default. Other paths, such as include directories, can be specified in the `includeGuardRoots` group. If a path matches, that string will be truncated from the include guard pattern.

For example, given a file at `allwpilib/src/main/native/include/wpiutil/support/ConcurrentQueue.h` and an include path of `src/main/native/include/`, the resulting include guard would be `ALLWPILIB_WPIUTIL_SUPPORT_CONCURRENTQUEUE_H_`.

The `repoRootNameOverride` group allows one to override the repository name used in include guards. This is useful for giving subprojects within one repository different repository roots in their include guards. Only specify one name in this group because subsequent names will be ignored.

## .wpiformat-license

This file contains the license header template. It should contain `Copyright (c)` followed by the company name and the string `{year}`. See the `.wpiformat-license` file in the docs/examples directory.

wpiformat checks the currently processed file's directory for a `.wpiformat` file first and traverses up the directory tree if one isn't found. This allows templates which are closer to the processed file to override a project's main template.

### License header semantics

The license header is always at the beginning of the file and ends after two newlines. If there isn't one, or it doesn't contain the required copyright contents, wpiformat inserts a new one containing the current year.

### `.wpiformat-license` special variables

`{year}` is replaced with a year range from the earliest copyright year in the file to the current year. If the earliest year is the current year, only that year will be written.

`{padding}` is optional and represents an expanding space which pads the line to 80 columns. Multiple instances of `{padding}` on the same line share the padding equally.
