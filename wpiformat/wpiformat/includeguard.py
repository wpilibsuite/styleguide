"""This task makes include guards follow the style stipulated by the Google
style guide.
"""

import os
import regex

from enum import Enum
from wpiformat.task import Task


class State(Enum):
    FINDING_IFNDEF = 1
    FINDING_ENDIF = 2
    DONE = 3


class IncludeGuard(Task):

    def should_process_file(self, config_file, name):
        return config_file.is_header_file(name)

    def run_pipeline(self, config_file, name, lines):
        linesep = Task.get_linesep(lines)
        lines_list = lines.split(linesep)
        output_list = lines_list

        state = State.FINDING_IFNDEF
        ifndef_regex = regex.compile("#ifndef \w+", regex.ASCII)
        define_regex = regex.compile("#define \w+", regex.ASCII)

        if_preproc_count = 0
        for i in range(len(lines_list)):
            if state == State.FINDING_IFNDEF:
                if lines_list[i].lstrip().startswith("#ifndef ") and \
                    lines_list[i + 1].lstrip().startswith("#define "):
                    state = State.FINDING_ENDIF

                    guard = self.make_include_guard(config_file, name)
                    output_list[i] = ifndef_regex.sub("#ifndef " + guard,
                                                      lines_list[i])
                    output_list[i + 1] = define_regex.sub(
                        "#define " + guard, lines_list[i + 1])
                    if_preproc_count += 1
                elif lines_list[i].lstrip().startswith("#pragma once"):
                    state = State.DONE
            elif state == State.FINDING_ENDIF:
                if "#if" in lines_list[i]:
                    if_preproc_count += 1
                elif "#endif" in lines_list[i]:
                    if_preproc_count -= 1

                if if_preproc_count == 0:
                    state = State.DONE
                    output_list[i] = "#endif  // " + guard
                else:
                    output_list[i] = lines_list[i]
            else:
                output_list[i] = lines_list[i]

        # If include guard not found
        if state == State.FINDING_IFNDEF:
            print("Error: " + name +
                  ": doesn't contain include guard or '#pragma once'")
            return (lines, False, False)

        output = linesep.join(output_list).rstrip() + linesep

        if output != lines:
            return (output, True, True)
        else:
            return (lines, False, True)

    def make_include_guard(self, config_file, name):
        """Returns properly formatted include guard based on repository root and
        file name.

        Keyword arguments:
        config_file -- Config object
        name -- file name string
        """
        repo_root_name_override = config_file.group("repoRootNameOverride")

        repo_root = Task.get_repo_root()
        guard_root = os.path.relpath(name, repo_root)
        if not repo_root_name_override:
            guard_path = os.path.basename(repo_root) + os.sep
        else:
            guard_path = repo_root_name_override[0] + os.sep
        include_roots = config_file.group("includeGuardRoots")

        if include_roots:
            prefix = ""
            for include_root in include_roots:
                if guard_root.startswith(
                        include_root) and len(include_root) > len(prefix):
                    prefix = include_root
            guard_path += guard_root[len(prefix):]
            return (regex.sub("[^a-zA-Z0-9]", "_", guard_path).upper() +
                    "_").lstrip("_")

        # No include guard roots matched, so append full name
        guard_path += guard_root
        return regex.sub("[^a-zA-Z0-9]", "_", guard_path).upper() + "_"
