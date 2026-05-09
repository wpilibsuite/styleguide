# wpiformat

Provides linters and formatters for ensuring WPILib's C++, Java, and Python code conform to its style guide. WPILib uses a variant of the Google style guides.

## Project Setup

To use wpiformat with a new project, copy `.wpiformat-license` from the examples folder into the project. If you're using C or C++, also create a new `.clang-format` file based on the desired C/C++ style.

## Supported tasks

|Name|File types|Description|
|----|----------|-----------|
|BraceComment|C, C++|Ensures the trailing comment on the closing brace of extern and namespace declarations matches the declaration name.|
|CIdentList|C|Replaces empty identifier lists `()` with `(void)`.|
|ClangFormat|C, C++|Runs clang-format.|
|ClangTidy|C, C++|Runs clang-tidy.|
|CMakeFormat|CMake|Runs gersemi.|
|EofNewline|all|Ensures that the file has zero EOF newlines if it's empty or one EOF newline.|
|GTestName|C, C++|Ensures Google Test test names follow the format `TEST(ThingTest, Thing)`.|
|IncludeGuard|C header, C++ header|Makes include guards follow the Google style guide.|
|JavaClass|Java|Removes extra newlines after the line containing `class`.|
|Jni|C++ source|Formats JNI signatures according to javah's output.|
|LicenseUpdate|C, C++, Java|Updates the license header at the top of the file.|
|Lint|C++|Runs cpplint.py.|
|PyFormat|Python|Runs black.|
|UsingDeclaration|C++ header|Disallows `using` declarations in header global namespaces.|
|UsingNamespaceStd|C++|Warns against `using namespace std;`.|
|Whitespace|all|Removes trailing whitespace.|

## .wpiformat

This file contains groups of filename regular expressions.
```
groupName {
  regex_here
}
```

The regexes are matched using [re.search()](https://docs.python.org/3/library/re.html#re.search), so they don't have to match a file's whole path.

Empty config groups can be omitted. Directory separators must be `/`, not `\`. During processing, they will be replaced internally with an `os.sep` that is automatically escaped for regexes.

wpiformat checks the currently processed file's directory for a `.wpiformat` file first and traverses up the directory tree if one isn't found. This allows configs which are closer to the processed file to override a project's main config.

### Specifying files to format

wpiformat has the following file extension associations: `.h` for C header files, `.c` for C source files, `.hpp` for C++ header files, `.cpp` for C++ source files, `.py` for Python files, and `.java` for Java files. Additional C and C++ files can be associated with the following groups:

- `cHeaderFileInclude`
- `cppHeaderFileInclude`
- `cppSrcFileInclude`

It's common to match just the file extension like so:
```
cppHeaderFileInclude {
  \.inc$
}
```

### Ignoring files

There are two groups of regexes which prevent tasks (i.e., formatters and linters) from running on matching files:

- `generatedFileExclude` (generated files)
- `modifiableFileExclude` (modifiable files)

Generated files should not be modified by the user; if they are, wpiformat will emit warnings. No warnings are emitted for modifications to modifiable files. Exclusion groups take precedence over inclusion groups.

Files excluded from version control via [.gitignore](https://git-scm.com/docs/gitignore) are skipped as modifiable.

The following file types are skipped as modifiable due to significant trailing whitespace:

- .jinja
- .patch

The following binary file types are skipped as modifiable:

- .dll
- .flac
- .gif
- .icns
- .ico
- .jar
- .jpeg
- .jpg
- .m4a
- .mp3
- .mp4
- .pdf
- .png
- .rknn
- .so
- .svg
- .tflite
- .ttf
- .wav
- .webp
- .woff2

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

This file contains the license header template. It should contain `Copyright (c)` followed by the company name and the string `{year}`. See the `.wpiformat-license` file in the examples directory.

wpiformat checks the currently processed file's directory for a `.wpiformat-license` file first and traverses up the directory tree if one isn't found. This allows templates which are closer to the processed file to override a project's main template.

### License header semantics

The license header is always at the beginning of the file and ends after two newlines. If there isn't one, or it doesn't contain the required copyright contents, wpiformat inserts a new one containing the current year.

### `.wpiformat-license` special variables

`{year}` is replaced with a year range from the earliest copyright year in the file to the current year. If the earliest year is the current year, only that year will be written.
```
// Copyright (c) {year} Company Name. All Rights Reserved.
```

`{padding}` is optional and represents an expanding space which pads the line to 80 columns. Multiple instances of `{padding}` on the same line share the padding equally.
```
/*{padding}Company Name{padding}*/
```

`{filename}` is optional and represents the current file's path relative to the Git repository root. Path separators are normalized to forward slashes on all platforms.
