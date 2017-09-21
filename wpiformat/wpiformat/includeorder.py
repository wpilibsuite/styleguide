"""This task sorts C/C++ includes."""

import os
import re

from wpiformat.task import Task


class IncludeOrder(Task):

    def __init__(self):
        Task.__init__(self)

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

    def should_process_file(self, config_file, name):
        return config_file.is_cpp_file(name)

    def classify_header(self, config_file, include_line, file_name):
        """Classify the given header name and return the corresponding index.

        Keyword arguments:
        config_file -- Config object
        include_line -- regex Match object for include line
        file_name -- file name string

        Returns header classification index.
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
            config_file.is_cpp_src_file(file_name)

        if include_is_related:
            return 0
        elif include_line.group("name") in self.c_std:
            return 1
        elif self.c_sys_regex.search(include_line.group("header")):
            return 1
        elif include_line.group("name") in self.cpp_std:
            return 2
        elif include_line.group("open_bracket") == "<":
            return 3
        elif self.include_is_header(config_file, file_name, include_name):
            return 4
        else:
            return -1

    def include_is_header(self, config_file, file_name, include_name):
        """Return True if include name has header extension.

        Keyword arguments:
        config_file -- Config object
        file_name -- file name string
        include_name -- include name string

        Returns true if include name is a header.
        """
        if not config_file.is_header_file(include_name):
            print("Error: " + file_name + ": include '" + include_name + \
                "' has extension not in header list")
            return False
        else:
            return True

    def add_brackets(self, name_match, group_number):
        """Adds appropriate brackets around and "#include" before include name
        based on group number.

        Keyword arguments:
        name_match -- include name's regex Match object
        group_number -- include classification index

        Returns include name with approriate brackets and "#include" prefix.
        """
        if group_number >= 1 and group_number <= 3:
            return "#include <" + name_match.group("name") + ">" + \
                name_match.group("postfix")
        else:
            return "#include \"" + name_match.group("name") + "\"" + \
                name_match.group("postfix")

    def write_headers(self, includes, ifdef_blocks=[[], [], [], [], []]):
        """Write out includes from sets.

        Keyword arguments:
        includes -- list of include strings
        ifdef_blocks -- list of list of #ifdef blocks (default empty 2D list)

        Returns list of output lines.
        """
        output_list = []

        for i in range(5):
            if includes[i]:
                sublist = sorted(list(includes[i]))
                output_list.extend(sublist)
                output_list.append("")  # Delimits groups of includes

            # #ifdef blocks go after other includes
            if ifdef_blocks[i]:
                # Remove newline from last #endif
                output_list.append(self.linesep.join(ifdef_blocks[i]).rstrip())
                output_list.append("")  # Delimits groups of #ifdef blocks
        if output_list:
            del output_list[-1]  # Remove last newline
        return output_list

    def header_sort(self, config_file, lines_list, file_name, start, end,
                    ifdef_level):
        """Recursively parses within #ifdef blocks for header includes and sorts
        them.

        Keyword arguments:
        config_file -- Config object
        lines_list -- list of file contents delimited by line separator
        file_name -- file name string
        start -- starting line for recursion step
        end -- ending line for recursion step
        ifdef_level -- current recursion depth of #ifdefs

        Returns tuple of the following:
          sorted output
          list of flags of instances of header categories within #ifdef block
          the index of the last line processed
          whether all header includes had header extension
        """
        output_list = []

        # Using sets here eliminates duplicate includes
        includes = [set(), set(), set(), set(), set()]
        include_flags = [0, 0, 0, 0, 0]

        ifdef_blocks = [[], [], [], [], []]

        i = start
        while i < end:
            if "#ifdef" in lines_list[i]:
                ifdef_count = 1
                for j in range(i + 1, end):
                    if "#ifdef" in lines_list[j]:
                        ifdef_count += 1
                    elif "#endif" in lines_list[j]:
                        ifdef_count -= 1
                    if ifdef_count == 0:
                        # Add #ifdef or #else line
                        ifdef = lines_list[i] + self.linesep

                        suboutput, flags, idx, valid_headers = self.header_sort(
                            config_file, lines_list, file_name, i + 1, j,
                            ifdef_level + 1)
                        i = j

                        # If header failed to classify, return failure
                        if not valid_headers:
                            return (output_list, flags, i, False)

                        if suboutput:
                            ifdef += self.linesep.join(suboutput) + self.linesep

                        # Add #endif line
                        ifdef += lines_list[j]

                        # #endif gets an extra line separator
                        if "#endif" in lines_list[j]:
                            ifdef += self.linesep

                        for k in range(len(include_flags)):
                            include_flags[k] |= flags[k]

                        if sum(flags) == 1:
                            ifdef_idx = 0
                            for k in range(len(flags)):
                                if flags[k] == 1:
                                    ifdef_idx = k
                                    break

                            # Only one type of include, so add it to sorts
                            ifdef_blocks[ifdef_idx].append(ifdef)
                        else:
                            # Treat #ifdef as barrier and flush includes
                            output_list.extend(self.write_headers(includes))
                            output_list.append("")
                            includes = [set(), set(), set(), set(), set()]

                            output_list.append(ifdef)
                        break
            elif "#include" in lines_list[i]:
                if "NOLINT" in lines_list[i]:
                    # NOLINT is a barrier, so flush includes
                    written = self.write_headers(includes)
                    if written:
                        output_list.append(self.linesep.join(written))
                        includes = [set(), set(), set(), set(), set()]

                    # NOLINT line will have newlines above and below, unless it
                    # is the first line being processed.
                    if output_list and output_list[-1] != "":
                        output_list.append("")
                    output_list.append(lines_list[i])
                    output_list.append("")

                    i += 1
                    continue

                # Insert header into appropriate list
                include_line = self.header_regex.search(lines_list[i])

                idx = self.classify_header(config_file, include_line, file_name)
                if idx != -1:
                    includes[idx].add(self.add_brackets(include_line, idx))
                    include_flags[idx] = 1
                else:
                    # If header failed to classify, return failure
                    return (output_list, include_flags, i, False)
            elif ifdef_level > 0 and lines_list[i] != "":
                # Non-preprocessor statements within a #ifdef block don't mark
                # the end of header include processing, but act as barrier for
                # sorting.

                # Dump currently collected header includes to file.
                # include_flags isn't reset as well here because that info is
                # still valid and necessary for sorting.
                written = self.write_headers(includes)
                if written:
                    output_list.append(self.linesep.join(written))
                    includes = [set(), set(), set(), set(), set()]

                output_list.append(lines_list[i])
            elif lines_list[i].strip() != "":
                # Write headers and #ifdef blocks if found
                written = self.write_headers(includes, ifdef_blocks)
                if written:
                    output_list.extend(written)

                return (output_list, include_flags, i, True)
            i += 1

        # Write headers and #ifdef blocks if found
        written = self.write_headers(includes, ifdef_blocks)
        if written:
            output_list.extend(written)

        return (output_list, include_flags, i, True)

    def run_pipeline(self, config_file, name, lines):
        self.override_regexes = []

        # Compile include sorting override regexes
        for group in [
                "includeRelated", "includeCSys", "includeCppSys",
                "includeOtherLibs", "includeProject"
        ]:
            regex_str = config_file.regex(group)
            self.override_regexes.append(re.compile(regex_str))

        self.linesep = Task.get_linesep(lines)

        file_name = os.path.basename(name)

        lines_list = lines.splitlines()

        # Write lines from beginning of file to headers
        i = 0
        while i < len(lines_list) and ("#ifdef" not in lines_list[i] and
                                       "#include" not in lines_list[i]):
            i += 1
        output_list = lines_list[0:i]

        suboutput, flags, idx, valid_headers = self.header_sort(
            config_file, lines_list, file_name, i, len(lines_list), 0)
        i = idx

        # If header failed to classify, return failure
        if not valid_headers:
            return (lines, False, False)

        if suboutput:
            output_list.extend(suboutput)

        # Remove possible extra newline from #endif
        output_list[-1] = output_list[-1].rstrip()

        # Write rest of file
        output_list.append("")
        output_list.extend(lines_list[i:])

        output = self.linesep.join(output_list).rstrip() + self.linesep
        if output != lines:
            return (output, True, True)
        else:
            return (lines, False, True)
