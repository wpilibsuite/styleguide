"""This task sorts C/C++ includes."""

import os
import regex

from wpiformat.task import PipelineTask


class IncludeOrder(PipelineTask):
    def __init__(self):
        super().__init__()

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
        # From https://en.cppreference.com/w/cpp/header
        self.c_std = [
            # C compatibility headers
            "assert.h",
            "ctype.h",
            "errno.h",
            "fenv.h",
            "float.h",
            "inttypes.h",
            "limits.h",
            "locale.h",
            "math.h",
            "setjmp.h",
            "signal.h",
            "stdarg.h",
            "stddef.h",
            "stdint.h",
            "stdio.h",
            "stdlib.h",
            "string.h",
            "time.h",
            "uchar.h",
            "wchar.h",
            "wctype.h",
            # Special C compatibility headers
            "stdatomic.h",
            # Empty C headers
            "ccomplex",
            "complex.h",
            "ctgmath",
            "tgmath.h",
            # Meaningless C headers
            "ciso646",
            "cstdalign",
            "cstdbool",
            "iso646.h",
            "stdalign.h",
            "stdbool.h",
            # Unsupported C headers
            "stdatomic.h",
            "stdnoreturn.h",
            "threads.h",
        ]

        # Header type 1: C system headers
        self.c_sys_regex = regex.compile(r"<[a-z][A-Za-z0-9/_-]*\.h>")

        # Header type 2: C++ standard library headers
        # With the exception of a few C standard library headers above, they are
        # the only headers which use only lowercase and underscores, and don't
        # have a ".h" suffix
        self.cpp_std_regex = regex.compile(r"(<|\")[a-z0-9_]+(>|\")")

        # Header type 3: Other library headers
        # They use angle brackets (open_bracket group is angle bracket)
        #
        # Header type 4: Project headers
        # They use double quotes (all other headers)
        self.header_regex = regex.compile(
            r"(?P<comment>//\s*)?"
            r"\#include\s*"
            r"(?P<header>"
            r"(?P<open_bracket><|\")"
            r"(?P<name>[^>\"]*)"
            r"(?P<close_bracket>>|\"))"
            r"(?P<postfix>.*)$"
        )

    @staticmethod
    def should_process_file(config_file, name):
        return config_file.is_c_file(name) or config_file.is_cpp_file(name)

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
        include_is_related = include_base == file_base and (
            config_file.is_c_src_file(file_name)
            or config_file.is_cpp_src_file(file_name)
        )

        if include_is_related:
            return 0
        elif include_line.group("name") in self.c_std:
            return 1
        elif self.c_sys_regex.search(include_line.group("header")):
            return 1
        elif self.cpp_std_regex.search(include_line.group("header")):
            return 2
        elif include_line.group("open_bracket") == "<":
            return 3
        elif self.include_is_header(config_file, file_name, include_name):
            return 4
        else:
            return -1

    @staticmethod
    def include_is_header(config_file, file_name, include_name):
        """Return True if include name has header extension.

        Keyword arguments:
        config_file -- Config object
        file_name -- file name string
        include_name -- include name string

        Returns true if include name is a header.
        """
        if not config_file.is_header_file(include_name):
            print(
                "Error: "
                + file_name
                + ": include '"
                + include_name
                + "' has extension not in header list"
            )
            return False
        else:
            return True

    @staticmethod
    def rebuild_include(name_match, group_number):
        """Adds appropriate brackets around include name and "#include" before
        that based on group number.

        Keyword arguments:
        name_match -- include name's regex Match object
        group_number -- include classification index

        Returns include name with approriate brackets and "#include" prefix.
        """
        if 1 <= group_number <= 3:
            output = (
                "#include <"
                + name_match.group("name")
                + ">"
                + name_match.group("postfix")
            )
        else:
            output = (
                '#include "'
                + name_match.group("name")
                + '"'
                + name_match.group("postfix")
            )

        if name_match.group("comment"):
            return name_match.group("comment") + output
        else:
            return output

    @staticmethod
    def dedup_list(seq):
        """Remove duplicates from list while preserving order.

        Keyword arguments:
        seq -- list from which to deduplicate entries

        Returns deduplicated list.
        """
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    def write_headers(self, includes, ifdef_blocks=None):
        """Write out includes from sets.

        Keyword arguments:
        includes -- list of include strings
        ifdef_blocks -- list of list of #ifdef blocks (default empty 2D list)

        Returns list of output lines.
        """
        if ifdef_blocks is None:
            ifdef_blocks = [[], [], [], [], []]
        output_list = []

        for i in range(5):
            if includes[i]:
                sublist = sorted(includes[i], key=lambda include: include.group("name"))
                str_list = [self.rebuild_include(x, i) for x in sublist]
                output_list.extend(self.dedup_list(str_list))
                output_list.append("")  # Delimits groups of includes

            # #ifdef blocks go after other includes
            if ifdef_blocks[i]:
                # Remove newline from last #endif
                output_list.append(self.linesep.join(ifdef_blocks[i]).rstrip())
                output_list.append("")  # Delimits groups of #ifdef blocks
        if output_list:
            del output_list[-1]  # Remove last newline
        return output_list

    def header_sort(self, config_file, lines_list, file_name, start, end, ifdef_level):
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
          list of bools indicating header category presence within #ifdef block
          the index of the last line processed
          whether all header includes had header extension
        """
        output_list = []

        # Using sets here eliminates duplicate includes
        includes = [[], [], [], [], []]

        # List of bools indicating header category presence within #ifdef block
        includes_present = [False, False, False, False, False]

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

                        suboutput, inc_present, idx, valid_headers = self.header_sort(
                            config_file,
                            lines_list,
                            file_name,
                            i + 1,
                            j,
                            ifdef_level + 1,
                        )
                        i = j

                        # If header failed to classify, return failure
                        if not valid_headers:
                            return output_list, inc_present, i, False

                        if suboutput:
                            ifdef += self.linesep.join(suboutput) + self.linesep

                        # Add #endif line
                        ifdef += lines_list[j]

                        # #endif gets an extra line separator
                        if "#endif" in lines_list[j]:
                            ifdef += self.linesep

                        for k in range(len(includes_present)):
                            includes_present[k] |= inc_present[k]

                        # If there is only one type of include present
                        if sum(inc_present) == 1:
                            ifdef_idx = 0
                            for k in range(len(inc_present)):
                                if inc_present[k]:
                                    ifdef_idx = k
                                    break

                            # Only one type of include, so add it to sorts
                            ifdef_blocks[ifdef_idx].append(ifdef)
                        else:
                            # Treat #ifdef as barrier and flush includes
                            output_list.extend(self.write_headers(includes))
                            if output_list and not output_list[-1].endswith(
                                self.linesep
                            ):
                                # Only add newline if content exists in
                                # output_list that doesn't end in a newline,
                                # which needs to be delimited from the #ifdef
                                output_list.append("")
                            includes = [[], [], [], [], []]

                            output_list.append(ifdef)
                        break
            elif "#include" in lines_list[i]:
                include_line = self.header_regex.search(lines_list[i])
                if not include_line:
                    # Write headers and #ifdef blocks if found
                    written = self.write_headers(includes, ifdef_blocks)
                    if written:
                        output_list.extend(written)
                    return output_list, includes_present, i, True

                if "NOLINT" in lines_list[i]:
                    # NOLINT is a barrier, so flush includes
                    written = self.write_headers(includes)
                    if written:
                        output_list.append(self.linesep.join(written))
                        includes = [[], [], [], [], []]

                    # NOLINT line will have newlines above and below, unless it
                    # is the first line being processed.
                    if output_list and output_list[-1] != "":
                        output_list.append("")
                    output_list.append(lines_list[i])
                    output_list.append("")

                    i += 1
                    continue

                # Insert header into appropriate list
                idx = self.classify_header(config_file, include_line, file_name)
                if idx != -1:
                    if include_line.group("comment"):
                        print(
                            "Warning: "
                            + file_name
                            + ": include '"
                            + include_line.group("name")
                            + "' is commented out"
                        )
                    includes[idx].append(include_line)
                    includes_present[idx] = True
                else:
                    # If header failed to classify, return failure
                    return output_list, includes_present, i, False
            elif ifdef_level > 0 and lines_list[i] != "":
                # Non-preprocessor statements within a #ifdef block don't mark
                # the end of header include processing, but act as barrier for
                # sorting.

                # Dump currently collected header includes to file.
                # includes_present isn't reset as well here because that info is
                # still valid and necessary for sorting.
                written = self.write_headers(includes)
                if written:
                    output_list.append(self.linesep.join(written))
                    includes = [[], [], [], [], []]

                output_list.append(lines_list[i])
            elif lines_list[i].strip() != "":
                # Write headers and #ifdef blocks if found
                written = self.write_headers(includes, ifdef_blocks)
                if written:
                    output_list.extend(written)

                return output_list, includes_present, i, True
            i += 1

        # Write headers and #ifdef blocks if found
        written = self.write_headers(includes, ifdef_blocks)
        if written:
            output_list.extend(written)

        return output_list, includes_present, i, True

    def run_pipeline(self, config_file, name, lines):
        self.override_regexes = []

        # Compile include sorting override regexes
        for group in [
            "includeRelated",
            "includeCSys",
            "includeCppSys",
            "includeOtherLibs",
            "includeProject",
        ]:
            regex_str = config_file.regex(group)
            self.override_regexes.append(regex.compile(regex_str))

        self.linesep = super().get_linesep(lines)

        file_name = os.path.basename(name)

        lines_list = lines.splitlines()

        # Write lines from beginning of file to headers
        i = 0
        while i < len(lines_list) and (
            "#ifdef" not in lines_list[i] and "#include" not in lines_list[i]
        ):
            i += 1
        output_list = lines_list[0:i]

        suboutput, inc_present, idx, valid_headers = self.header_sort(
            config_file, lines_list, file_name, i, len(lines_list), 0
        )
        i = idx

        # If header failed to classify, return failure
        if not valid_headers:
            return lines, False

        if suboutput:
            output_list.extend(suboutput)

        # Remove extra empty lines from end of includes
        while len(output_list) > 0 and output_list[-1].rstrip() == "":
            del output_list[-1]  # Remove last newline

        # Remove possible extra newline from #endif
        if len(output_list) > 0:
            output_list[-1] = output_list[-1].rstrip()
            output_list.append("")

        # Write rest of file
        output_list.extend(lines_list[i:])

        output = self.linesep.join(output_list).rstrip() + self.linesep
        return output, True
