"""This task makes include guards follow the style stipulated by the Google
style guide.
"""

import os
import re

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
        ifndef_regex = re.compile("#ifndef \w+", re.ASCII)
        define_regex = re.compile("#define \w+", re.ASCII)

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

        # if include guard not found
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
        repo_root = Task.get_repo_root()

        name = os.path.relpath(name, repo_root)
        guard_path = os.path.basename(repo_root) + "/"
        include_roots = config_file.group("includeGuardRoots")

        if include_roots:
            for include_root in include_roots:
                if name.startswith(include_root):
                    guard_path += name[len(include_root):]
                    return re.sub("[^a-zA-Z0-9]", "_", guard_path).upper() + "_"

        # No include guard roots matched, so append full name
        guard_path += name
        return re.sub("[^a-zA-Z0-9]", "_", guard_path).upper() + "_"
