"""This task sorts C/C++ includes."""

import os
import re

from task import Task

class IncludeOrder(Task):
    def __init__(self):
        Task.__init__(self)

        self.c_std = ["assert.h", "complex.h", "ctype.h", "errno.h", "fenv.h",
                      "float.h", "inttypes.h", "iso646.h", "limits.h",
                      "locale.h", "math.h", "setjmp.h", "signal.h",
                      "stdalign.h", "stdarg.h", "stdatomic.h", "stdbool.h",
                      "stddef.h", "stdint.h", "stdio.h", "stdlib.h",
                      "stdnoreturn.h", "string.h", "tgmath.h", "threads.h",
                      "time.h", "uchar.h", "wchar.h", "wctype.h"]

        self.cpp_std = ["cstdlib", "csignal", "csetjmp", "cstdarg", "typeinfo",
                        "typeindex", "type_traits", "bitset", "functional",
                        "utility", "ctime", "chrono", "cstddef",
                        "initializer_list", "tuple", "new", "memory",
                        "scoped_allocator", "climits", "cfloat", "cstdint",
                        "cinttypes", "limits", "exception", "stdexcept",
                        "cassert", "system_error", "cerrno", "cctype",
                        "cwctype", "cstring", "cwchar", "cuchar", "string",
                        "array", "vector", "deque", "list", "forward_list",
                        "set", "map", "unordered_set", "unordered_map",
                        "stack", "queue", "algorithm", "iterator", "cmath",
                        "complex", "valarray", "random", "numeric", "ratio",
                        "cfenv", "iosfwd", "ios", "istream", "ostream",
                        "iostream", "fstream", "sstream", "strstream",
                        "iomanip", "streambuf", "cstdio", "locale", "clocale",
                        "codecvt", "regex", "atomic", "thread", "mutex",
                        "shared_mutex", "future", "condition_variable",
                        "ciso646", "ccomplex", "ctgmath", "cstdalign",
                        "cstdbool"]

        # All other headers matching this pattern are C system headers
        self.c_sys_regex = re.compile("<.*\.h>")

        self.header_regex = re.compile("(?P<header>"
                                         "(?P<open_bracket><|\")"
                                         "(?P<name>.*)"
                                         "(?P<close_bracket>>|\"))"
                                       "(?P<postfix>.*)")

    def get_file_extensions(self):
        return Task.get_config("cppHeaderExtensions") + \
            Task.get_config("cppSrcExtensions")

    def run(self, name, lines):
        self.name = name

        includes = [[], [], [], [], []]
        found_includes = False

        lines_list = lines.splitlines()
        include_start = 0
        include_stop = len(lines_list)

        ifdef_blocks = []
        ifdef_count = 0
        in_ifdef = False

        override_regexes = []

        # Compile include sorting override regexes
        for group in ["includeRelated", "includeCSys", "includeCppSys",
                    "includeOtherLibs", "includeProject"]:
            if not len(Task.get_config(group)):
                override_regexes.append(re.compile("a^"))
            else:
                regex_str = "(" + "|".join(Task.get_config(group)) + ")"

                # On Windows, fix forward slash for include regexes
                if os.sep == "\\":
                    regex_str = regex_str.replace("\\\\", "/")

                override_regexes.append(re.compile(regex_str))

        # Retrieve includes
        for line_count in range(0, len(lines_list)):
            if not in_ifdef and "#ifdef" in lines_list[line_count]:
                if not found_includes:
                    include_start = line_count
                    found_includes = True

                in_ifdef = True
                ifdef_blocks.append([lines_list[line_count]])
            elif in_ifdef and "#endif" in lines_list[line_count]:
                in_ifdef = False
                ifdef_blocks[ifdef_count].append(lines_list[line_count])
                ifdef_count = ifdef_count + 1
            elif in_ifdef:
                ifdef_blocks[ifdef_count].append(lines_list[line_count])
            else:
                valid_preproc = \
                    lines_list[line_count].strip() == "" or \
                    "#include" in lines_list[line_count] or in_ifdef

                if found_includes and not valid_preproc:
                    include_stop = line_count
                    break

                if "#include" in lines_list[line_count]:
                    if not found_includes:
                        include_start = line_count
                        found_includes = True

                    # Insert header into apprioriate list. NOLINT lines are
                    # placed in the first group since maintaining the header's
                    # relative ordering beyond that is not feasible.
                    name = self.header_regex.search(lines_list[line_count])
                    include_name = \
                        os.path.splitext(os.path.basename(name.group("name")))
                    file_name = os.path.splitext(os.path.basename(self.name))

                    # Process override regexes
                    include_overriden = False
                    for override_count in range(0, 5):
                        if override_regexes[override_count].search(
                                name.group("name")):
                            fixed_name = \
                                self.fixup_include(name, override_count)
                            includes[override_count].append(fixed_name)
                            include_overriden = True

                    if include_overriden:
                        continue

                    # Is related if include has same base name as file name and
                    # file has a source extension
                    include_is_related = include_name[0] == file_name[0] and \
                        file_name[1][1:] in Task.get_config("cppSrcExtensions")

                    if include_is_related or "NOLINT" in lines_list[line_count]:
                        includes[0].append(self.fixup_include(name, 0))
                    elif name.group("name") in self.c_std:
                        includes[1].append(self.fixup_include(name, 1))
                    elif self.c_sys_regex.search(name.group("header")):
                        includes[1].append(self.fixup_include(name, 1))
                    elif name.group("name") in self.cpp_std:
                        includes[2].append(self.fixup_include(name, 2))
                    elif name.group("open_bracket") == "<":
                        includes[3].append(self.fixup_include(name, 3))
                    else:
                        includes[4].append(self.fixup_include(name, 4))

        # If no includes were found, write whole file as-is
        if not found_includes:
            output_list = lines_list
        else:
            # Sort include lists
            for sublist in includes:
                sublist.sort()

            # Write out includes
            output_list = lines_list[0:include_start]
            for include_count in range(0, len(includes)):
                if len(includes[include_count]):
                    output_list.extend(includes[include_count])
                    output_list.append("")  # Delimits groups of includes

            # ifdef blocks go after all other includes
            if ifdef_blocks != [[]]:
                for block in ifdef_blocks:
                    output_list.append(os.linesep.join(block))
                    output_list.append("")

            output_list.extend(lines_list[include_stop:])

        output = os.linesep.join(output_list).rstrip() + os.linesep
        if output != lines:
            return (output, True, True)
        else:
            return (lines, False, True)

    def fixup_include(self, name_match, group_number):
        if group_number == 1 or group_number == 2 or group_number == 3:
            return "#include <" + name_match.group("name") + ">" + \
                name_match.group("postfix")
        else:
            return "#include \"" + name_match.group("name") + "\"" + \
                name_match.group("postfix")
