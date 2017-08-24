"""This task sorts C/C++ includes."""

import os
import re

from . import task


class IncludeOrder(task.Task):

    def __init__(self):
        task.Task.__init__(self)

        # There are 5 header groups:
        # 0. Related headers
        # 1. C system headers (includes standard library headers)
        # 2. C++ system headers (includes standard library headers)
        # 3. Other library headers
        # 4. Project headers
        #
        # See comments below for how headers are classified.

        # Header type 0: Related headers
        # Base name of include matches base name of current file

        # Header type 1: C standard library headers
        self.c_std = [
            "assert.h", "complex.h", "ctype.h", "errno.h", "fenv.h", "float.h",
            "inttypes.h", "iso646.h", "limits.h", "locale.h", "math.h",
            "setjmp.h", "signal.h", "stdalign.h", "stdarg.h", "stdatomic.h",
            "stdbool.h", "stddef.h", "stdint.h", "stdio.h", "stdlib.h",
            "stdnoreturn.h", "string.h", "tgmath.h", "threads.h", "time.h",
            "uchar.h", "wchar.h", "wctype.h"
        ]

        # Header type 1: C system headers
        self.c_sys_regex = re.compile("<[a-z][A-Za-z0-9/_-]*\.h>")

        # Header type 2: C++ standard library headers
        self.cpp_std = [
            "cstdlib", "csignal", "csetjmp", "cstdarg", "typeinfo", "typeindex",
            "type_traits", "bitset", "functional", "utility", "ctime", "chrono",
            "cstddef", "initializer_list", "tuple", "new", "memory",
            "scoped_allocator", "climits", "cfloat", "cstdint", "cinttypes",
            "limits", "exception", "stdexcept", "cassert", "system_error",
            "cerrno", "cctype", "cwctype", "cstring", "cwchar", "cuchar",
            "string", "array", "vector", "deque", "list", "forward_list", "set",
            "map", "unordered_set", "unordered_map", "stack", "queue",
            "algorithm", "iterator", "cmath", "complex", "valarray", "random",
            "numeric", "ratio", "cfenv", "iosfwd", "ios", "istream", "ostream",
            "iostream", "fstream", "sstream", "strstream", "iomanip",
            "streambuf", "cstdio", "locale", "clocale", "codecvt", "regex",
            "atomic", "thread", "mutex", "shared_mutex", "future",
            "condition_variable", "ciso646", "ccomplex", "ctgmath", "cstdalign",
            "cstdbool"
        ]

        # Header type 3: Other library headers
        # They use angle brackets (open_bracket group is angle bracket)
        #
        # Header type 4: Project headers
        # They use double quotes (all other headers)
        self.header_regex = re.compile("(?P<header>"
                                       "(?P<open_bracket><|\")"
                                       "(?P<name>.*)"
                                       "(?P<close_bracket>>|\"))"
                                       "(?P<postfix>.*)")

        self.override_regexes = []

        # Compile include sorting override regexes
        for group in [
                "includeRelated", "includeCSys", "includeCppSys",
                "includeOtherLibs", "includeProject"
        ]:
            regex_str = task.group_to_regex(group)
            self.override_regexes.append(re.compile(regex_str))

    def should_process_file(self, name):
        extensions = task.get_config("cppHeaderExtensions") + \
            task.get_config("cppSrcExtensions")

        return any(name.endswith("." + ext) for ext in extensions)

    def classify_header(self, include_line, file_name):
        """Classify the given header name and return the corresponding index.
        """
        # Process override regexes
        for idx in range(5):
            if self.override_regexes[idx].search(include_line.group("name")):
                return idx

        include_name = os.path.basename(include_line.group("name"))
        include_base, include_ext = os.path.splitext(include_name)
        file_base, file_ext = os.path.splitext(file_name)

        # Is related if include has same base name as file name and file has a
        # source extension
        include_is_related = include_base == file_base and \
            file_ext[1:] in task.get_config("cppSrcExtensions")

        # NOLINT lines are placed in the first group since maintaining the
        # header's relative ordering beyond that is not feasible.
        if include_is_related or "NOLINT" in include_line.group("postfix"):
            return 0
        elif include_line.group("name") in self.c_std:
            return 1
        elif self.c_sys_regex.search(include_line.group("header")):
            return 1
        elif include_line.group("name") in self.cpp_std:
            return 2
        elif include_line.group("open_bracket") == "<":
            return 3
        elif self.include_is_header(file_name, include_name):
            return 4
        else:
            return -1

    def include_is_header(self, file_name, include_name):
        """Return True if include name has header extension.
        """
        base, ext = os.path.splitext(include_name)
        if ext[1:] not in task.get_config("cppHeaderExtensions"):
            print("Error: " + file_name + ": include '" + include_name + \
                "' has extension not in header list")
            return False
        else:
            return True

    def add_brackets(self, name_match, group_number):
        """Adds appropriate brackets around and "#include" before include name
        based on group number.
        """
        if group_number >= 1 and group_number <= 3:
            return "#include <" + name_match.group("name") + ">" + \
                name_match.group("postfix")
        else:
            return "#include \"" + name_match.group("name") + "\"" + \
                name_match.group("postfix")

    def run(self, name, lines):
        linesep = task.get_linesep(lines)

        file_name = os.path.basename(name)

        # Using sets here eliminates duplicate includes
        includes = [set(), set(), set(), set(), set()]
        found_includes = False

        lines_list = lines.splitlines()
        include_stop = len(lines_list)

        ifdef_blocks = []
        in_ifdef = False

        # Retrieve includes
        for line_idx in range(len(lines_list)):
            if not in_ifdef and "#ifdef" in lines_list[line_idx]:
                if not found_includes:
                    found_includes = True

                    # Write from beginning of file to includes
                    output_list = lines_list[0:line_idx]

                in_ifdef = True
                ifdef_blocks.append(lines_list[line_idx])
            elif in_ifdef and "#endif" in lines_list[line_idx]:
                in_ifdef = False
                ifdef_blocks.append(lines_list[line_idx])
                ifdef_blocks.append("")
            elif in_ifdef:
                ifdef_blocks.append(lines_list[line_idx])
            else:
                valid_preproc = \
                    lines_list[line_idx].strip() == "" or \
                    "#include" in lines_list[line_idx] or in_ifdef

                if found_includes and not valid_preproc:
                    include_stop = line_idx
                    break

                if "#include" in lines_list[line_idx]:
                    if not found_includes:
                        found_includes = True

                        # Write from beginning of file to includes
                        output_list = lines_list[0:line_idx]

                    # Insert header into apprioriate list
                    include_line = \
                        self.header_regex.search(lines_list[line_idx])

                    idx = self.classify_header(include_line, file_name)
                    if idx != -1:
                        includes[idx].add(self.add_brackets(include_line, idx))
                    else:
                        return (lines, False, False)

        # If no includes were found, write whole file as-is
        if not found_includes:
            output_list = lines_list
        else:
            # Write out includes
            for subset in includes:
                if len(subset):
                    sublist = sorted(list(subset))
                    output_list.extend(sublist)
                    output_list.append("")  # Delimits groups of includes

            # ifdef blocks go after all other includes
            if ifdef_blocks:
                output_list.append(linesep.join(ifdef_blocks))

            output_list.extend(lines_list[include_stop:])

        output = linesep.join(output_list).rstrip() + linesep
        if output != lines:
            return (output, True, True)
        else:
            return (lines, False, True)
