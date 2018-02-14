"""This task warns against "using namespace std;"."""

import regex

from wpiformat.task import Task


class UsingNamespaceStd(Task):

    def should_process_file(self, config_file, name):
        return config_file.is_cpp_file(name)

    def run_pipeline(self, config_file, name, lines):
        linesep = Task.get_linesep(lines)

        # Find instances of "using namespace std;" or subnamespaces of "std",
        # but not std::literals or std::chrono_literals.
        using_regex = regex.compile(
            "using\s+namespace\s+std(;|::(?!(chrono_)?literals|placeholders))")

        for match in using_regex.finditer(lines):
            linenum = lines.count(linesep, 0, match.start()) + 1
            print(
                "Warning: " + name + ": " + str(linenum) +
                ": avoid \"using namespace std;\" in production software. While it is used in introductory C++, it pollutes the global namespace with standard library symbols."
            )

        return (lines, False, True)
