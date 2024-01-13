"""This task replaces empty C identifier lists "()" with "(void)"."""

import regex

from wpiformat.task import PipelineTask


class CIdentList(PipelineTask):
    @staticmethod
    def __print_failure(name):
        print(
            "Error: " + name + ": unmatched curly braces when scanning for "
            "C identifier lists. If the code compiles, this is a bug in "
            "wpiformat."
        )

    @staticmethod
    def should_process_file(config_file, name):
        return config_file.is_c_file(name) or config_file.is_cpp_file(name)

    def run_pipeline(self, config_file, name, lines):
        linesep = super().get_linesep(lines)

        output = ""
        pos = 0

        # C files use C linkage by default
        is_c = config_file.is_c_file(name)

        # Tokenize as extern "C" or extern "C++" with optional {, open brace,
        # close brace, or () folllowed by { to disambiguate function calls.
        # extern is first to try matching a brace to it before classifying the
        # brace as generic.
        #
        # Valid function prototypes and definitions have return type, spaces,
        # function name, optional spaces, then braces. They are followed by ; or
        # {.
        #
        # "def\\s+\w+" matches preprocessor directives "#ifdef" and "#ifndef" so
        # their contents aren't used as a return type.
        #
        # "\w+\**\s+\w+\s*" matches a function return type with 0 or more
        # trailing asterisks, spaces, a function name, then spaces before the
        # open parenthesis
        preproc_str = r"#else|#endif|"
        comment_str = r"/\*|\*/|//|" + linesep + r"|"
        string_str = r"\\\\|\\\"|\"|"
        char_str = r"\\'|'|"
        extern_str = r"(?P<ext_decl>extern \"C(\+\+)?\")\s+(?P<ext_brace>\{)?|"
        braces_str = r"\{|\}|;|def\s+\w+|\w+\**\s+\w+\s*(?P<paren>\(\))"
        postfix_str = r"(?=\s*(;|\{))"
        token_regex = regex.compile(
            preproc_str
            + comment_str
            + string_str
            + char_str
            + extern_str
            + braces_str
            + postfix_str
        )

        EXTRA_POP_OFFSET = 2

        # If value is greater than pop offset, the value needs to be restored in
        # addition to an extra stack pop being performed. The pop offset is
        # removed before assigning to is_c.
        #
        # is_c + pop offset == 2: C lang restore that needs extra brace pop
        # is_c + pop offset == 3: C++ lang restore that needs extra brace pop
        extern_brace_indices = [is_c]

        in_preproc_else = False
        in_multicomment = False
        in_singlecomment = False
        in_string = False
        in_char = False
        for match in token_regex.finditer(lines):
            token = match.group()

            # Skip #else to #endif in case they have braces in them. This
            # assumes preprocessor directives are only used for conditional
            # compilation for different platforms and have the same amount of
            # braces in both branches. Nested preprocessor directives are also
            # not handled.
            if token == "#else":
                in_preproc_else = True
            elif token == "#endif":
                in_preproc_else = False
            if in_preproc_else:
                continue

            if token == "/*":
                if not in_singlecomment and not in_string and not in_char:
                    in_multicomment = True
            elif token == "*/":
                if not in_singlecomment and not in_string and not in_char:
                    in_multicomment = False
            elif token == "//":
                if not in_multicomment and not in_string and not in_char:
                    in_singlecomment = True
            elif in_singlecomment and linesep in token:
                # Ignore token if it's in a singleline comment. Only check it
                # for newlines to end the comment.
                in_singlecomment = False
            elif in_multicomment or in_singlecomment:
                # Tokens processed after this branch are ignored if they are in
                # comments
                continue
            elif token == '\\"':
                continue
            elif token == '"':
                if not in_char:
                    in_string = not in_string
            elif token == "\\'":
                continue
            elif token == "'":
                if not in_string:
                    in_char = not in_char
            elif in_string or in_char:
                # Tokens processed after this branch are ignored if they are in
                # double or single quotes
                continue
            elif token == "{":
                extern_brace_indices.append(is_c)
            elif token == "}":
                is_c = extern_brace_indices.pop()

                if len(extern_brace_indices) == 0:
                    self.__print_failure(name)
                    return lines, False

                # If the next stack frame is from an extern without braces, pop
                # it.
                if extern_brace_indices[-1] >= EXTRA_POP_OFFSET:
                    is_c = extern_brace_indices[-1] - EXTRA_POP_OFFSET
                    extern_brace_indices.pop()
            elif token == ";":
                if len(extern_brace_indices) == 0:
                    self.__print_failure(name)
                    return lines, False

                # If the next stack frame is from an extern without braces, pop
                # it.
                if extern_brace_indices[-1] >= EXTRA_POP_OFFSET:
                    is_c = extern_brace_indices[-1] - EXTRA_POP_OFFSET
                    extern_brace_indices.pop()
            elif token.startswith("extern"):
                # Back up language setting first
                if match.group("ext_brace"):
                    extern_brace_indices.append(is_c)
                else:
                    # Handling an extern without braces changing the language
                    # type is done by treating it as a pseudo-brace that gets
                    # popped as well when the next "}" or ";" is encountered.
                    # The "extra pop" offset is used as a flag on the top stack
                    # value that is checked whenever a pop is performed.
                    extern_brace_indices.append(is_c + EXTRA_POP_OFFSET)

                # Change language based on extern declaration
                if match.group("ext_decl") == 'extern "C"':
                    is_c = True
                else:
                    is_c = False
            elif match.group("paren") and "return " not in match.group() and is_c:
                # Replaces () with (void)
                output += lines[pos : match.span("paren")[0]] + "(void)"
                pos = match.span("paren")[0] + len("()")

        # Write rest of file if it wasn't all processed
        if pos < len(lines):
            output += lines[pos:]

        # Invariant: extern_brace_indices has one entry
        success = len(extern_brace_indices) == 1
        if not success:
            self.__print_failure(name)

        return output, success
