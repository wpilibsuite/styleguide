"""This task removes redundant "virtual" specifier instances.

When the "override" specifier is specified in a C++ function signature, the
"virtual" specifier is redundant because "override" implies "virtual".
"""

import regex

from wpiformat.task import Task


class VirtualSpecifier(Task):

    def should_process_file(self, config_file, name):
        return config_file.is_cpp_file(name)

    def run_pipeline(self, config_file, name, lines):
        linesep = Task.get_linesep(lines)

        file_changed = False
        output = ""

        # Function signature parts
        virtual_spec = r"(?P<virtual>virtual\s+)?"
        return_type = r"(?P<return_type>[\w,\*&]+\s+)"
        func_args = r"(?P<func_args>\([^\)]*\)(\s*const)?)"
        specifiers = r"(?P<specifiers>[^;{]*)?"

        # Construct regexes for function signatures
        regexes = []
        regexes.append(
            regex.compile(virtual_spec + r"(?P<func_sig>" + return_type +
                          r"(?P<func_name>\w+\s*)" + func_args + ")" +
                          specifiers))
        regexes.append(
            regex.compile(virtual_spec + r"(?P<func_sig>" +
                          r"(?P<func_name>[\w~]+\s*)" + func_args + ")" +
                          specifiers))

        for rgx in regexes:
            pos = 0
            for match in rgx.finditer(lines):
                # Append lines before match
                output += lines[pos:match.start()]

                # Append virtual specifier if it's not redundant
                if "final" not in match.group(
                        "specifiers") and "override" not in match.group(
                            "specifiers"):
                    if match.group("virtual"):
                        output += match.group("virtual")
                else:
                    file_changed = True
                output += match.group("func_sig")

                # Strip redundant specifiers
                specifiers_in = match.group("specifiers")
                specifiers_out = specifiers_in
                if "final" in specifiers_out:
                    specifiers_out = regex.sub(r"\s+override", "",
                                               specifiers_out)
                if specifiers_in != specifiers_out:
                    file_changed = True
                output += specifiers_out

                pos = match.end()

            # Append leftover lines in file
            if pos < len(lines):
                output += lines[pos:]

            # Reset line buffer for next regex
            lines = output
            output = ""

        return (lines, file_changed, True)
