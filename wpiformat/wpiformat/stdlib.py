"""This task replaces C standard library includes with C++ equivalents. stdint.h
and assert.h are exceptions.
"""

import regex

from wpiformat.task import Task


class Header(object):

    def __init__(self, name, func_names=set(), type_regexes=[],
                 add_prefix=True):
        """Manages function and type names in standard library header.

        Keyword arguments:
        name -- header name string
        func_names -- set of function name strings (default set())
        type_regexes -- list of type regex strings (default [])
        add_prefix -- determines whether std:: prefix is added or removed
                      (default True)
        """
        self.name = name
        self.func_names = func_names
        self.add_prefix = add_prefix

        regex_prefix = ""
        if add_prefix:
            self.prefix = "std::"
            self.type_sub = "std::\g<1>"
            regex_prefix = ""
        else:
            self.prefix = ""
            self.type_sub = "\g<1>"
            regex_prefix = "std::"

        if func_names != []:
            # Matches C standard library function uses. C standard library
            # function names are alphanumeric and start with a letter. If the
            # function name is preceded by a word character and a space, it's
            # a function definition instead of a usage.
            self.func_regex = regex.compile(
                "(?:[^\w]\s+|,|\()"
                +  # Preceded by nonword character and spaces, comma, or "("
                regex_prefix + "([a-z][a-z0-9]*)" +  # C stdlib function name
                "(?:\()"  # Followed by open parenthesis
            )
        else:
            self.func_regex = None

        if type_regexes != []:
            # Check for type uses

            # Preceded by beginning of file, "<" (template), " ", ",", "(", or
            # line separator and optional spaces
            lookbehind = "(?<=^|\<| |,|\(|\n)"

            type_names = regex_prefix + "(" + "|".join(type_regexes) + ")"

            # Followed by optional spaces and ">", ")", ",", ";", or pointer
            # asterisks
            lookahead = "(?=(\s*(\>|\)|,|;|\*+))|\s)"

            self.type_regex = regex.compile(lookbehind + type_names + lookahead)
        else:
            self.type_regex = None


class Stdlib(Task):

    def __init__(self):
        Task.__init__(self)

        self.headers = []

        # assert is a macro, so it's ommitted to avoid prefixing with std::
        self.headers.append(Header("assert"))

        self.headers.append(
            Header(
                "ctype", {
                    "isalum", "isalpha", "isblank", "iscntrl", "isdigit",
                    "isgraph", "islower", "isprint", "ispunct", "isspace",
                    "isupper", "isxdigit", "tolower", "toupper"
                }))
        self.headers.append(Header("errno"))
        self.headers.append(Header("float"))
        self.headers.append(Header("limits"))
        self.headers.append(
            Header(
                "math", {
                    "cos", "acos", "cosh", "acosh", "sin", "asin", "asinh",
                    "tan", "atan", "atan2", "atanh", "exp", "frexp", "ldexp",
                    "log", "log10", "ilogb", "log1p", "log2", "logb", "modf",
                    "exp2", "expm1", "scalbl", "scalbln", "pow", "sqrt", "cbrt",
                    "hypot", "erf", "erfc", "tgamma", "lgamma", "ceil", "floor",
                    "fmod", "trunc", "round", "lround", "llround", "rint",
                    "lrint", "llrint", "nearbyint", "remainder", "remquo",
                    "copysign", "nan", "nextafter", "nexttoward", "fdim",
                    "fmax", "fmin", "fma", "fpclassify", "abs", "fabs",
                    "signbit", "isfinite", "isinf", "isnan", "isnormal",
                    "isgreater", "isgreaterequal", "isless", "islessequal",
                    "islessgreater", "isunordered"
                }))
        self.headers.append(
            Header("setjmp", {"longjmp", "setjmp"}, ["jmp_buf"]))
        self.headers.append(
            Header("signal", {"signal", "raise"}, ["sig_atomic_t"], False))
        self.headers.append(Header("stdarg", {"va_list"}))
        self.headers.append(
            Header("stddef", type_regexes=["(ptrdiff|max_align|nullptr)_t"]))

        # size_t isn't actually defined in stdint, but it fits best here for
        # removing the std:: prefix
        self.headers.append(
            Header(
                "stdint",
                type_regexes=[
                    "((u?int((_fast|_least)?(8|16|32|64)|max|ptr)|size)_t)"
                ],
                add_prefix=False))

        self.headers.append(
            Header(
                "stdio", {
                    "remove", "rename", "rewind", "tmpfile", "tmpnam", "fclose",
                    "fflush", "fopen", "freopen", "fgetc", "fgets", "fputc",
                    "fputs", "fread", "fwrite", "fgetpos", "fseek", "fsetpos",
                    "ftell", "feof", "ferror", "setbuf", "setvbuf", "fprintf",
                    "snprintf", "sprintf", "vfprintf", "vprintf", "vsnprintf",
                    "vsprintf", "printf", "fscanf", "sscanf", "vfscanf",
                    "vscanf", "vsscanf", "scanf", "getchar", "gets", "putc",
                    "putchar", "puts", "getc", "ungetc", "clearerr", "perror"
                }, ["FILE", "fpos_t"]))
        self.headers.append(
            Header(
                "stdlib", {
                    "atof", "atoi", "atol", "atoll", "strtof", "strtol",
                    "strtod", "strtold", "strtoll", "strtoul", "strtoull",
                    "rand", "srand", "free", "calloc", "malloc", "realloc",
                    "abort", "at_quick_exit", "quick_exit", "atexit", "exit",
                    "getenv", "system", "_Exit", "bsearch", "qsort", "llabs",
                    "labs", "abs", "lldiv", "ldiv", "div", "mblen", "btowc",
                    "wctomb", "wcstombs", "mbstowcs"
                }, ["(l|ll)?div_t"]))
        self.headers.append(
            Header(
                "string", {
                    "memcpy", "memcmp", "memchr", "memmove", "memset", "strcpy",
                    "strncpy", "strcat", "strncat", "strcmp", "strncmp",
                    "strcoll", "strchr", "strrchr", "strstr", "strxfrm",
                    "strcspn", "strrspn", "strpbrk", "strtok", "strerror",
                    "strlen"
                }))
        self.headers.append(
            Header(
                "time", {
                    "clock", "asctime", "ctime", "difftime", "gmtime",
                    "localtime", "mktime", "strftime", "time"
                }, ["(clock|time)_t"]))

    def should_process_file(self, config_file, name):
        return config_file.is_cpp_file(name)

    def run_pipeline(self, config_file, name, lines):
        file_changed = False
        for header in self.headers:
            # Prepare include names
            before = ""
            after = ""
            if header.add_prefix:
                before = header.name + ".h"
                after = "c" + header.name
            else:
                before = "c" + header.name
                after = header.name + ".h"

            if "#include <" + before + ">" in lines:
                if not file_changed:
                    file_changed = True
                lines = lines.replace("#include <" + before + ">",
                                      "#include <" + after + ">")

            if header.func_regex:
                (lines, changed) = self.func_substitute(header, lines)
                file_changed |= changed

            if header.type_regex:
                old_length = len(lines)
                lines = header.type_regex.sub(header.type_sub, lines)
                if not file_changed and old_length != len(lines):
                    file_changed = True

        return (lines, file_changed, True)

    def func_substitute(self, header, lines):
        """Returns modified lines and whether string changed.

        Keyword arguments:
        header -- Header object
        lines -- file contents string

        Returns tuple containing the following:
          modified file contents string
          whethr file contents changed
        """
        pos = 0
        lines_changed = False
        while pos < len(lines):
            old_length = len(lines)

            # Check for function starting at "pos"
            match = header.func_regex.search(lines, pos)
            if not match:
                break

            # Set "pos" to after current match
            pos = match.start(1) + len(header.prefix) + len(match.group(1))

            # If function name is part of this header, substitute its name
            if match.group(1) in header.func_names:
                lines = lines[0:match.start(1)] + header.prefix + \
                    match.group(1) + lines[match.end(1):]
                if not lines_changed and old_length != len(lines):
                    lines_changed = True
        return (lines, lines_changed)
