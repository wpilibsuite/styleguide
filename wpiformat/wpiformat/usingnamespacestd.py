"""This task warns against "using namespace std;"."""

import re

from wpiformat.config import Config
from wpiformat.task import PipelineTask


class UsingNamespaceStd(PipelineTask):
    @staticmethod
    def should_process_file(config_file: Config, filename: str) -> bool:
        return config_file.is_cpp_file(filename)

    def run_pipeline(
        self, config_file: Config, filename: str, lines: str
    ) -> tuple[str, bool]:
        linesep = super().get_linesep(lines)

        # Find instances of "using namespace std;" or subnamespaces of "std",
        # but not std::literals or std::chrono_literals.
        using_regex = re.compile(
            r"using\s+namespace\s+std(;|::(?!(chrono_|string_view_)?literals|placeholders))"
        )

        for match in using_regex.finditer(lines):
            linenum = lines.count(linesep, 0, match.start()) + 1
            print(
                f'warning: {filename}: {linenum}: avoid "using namespace std;" in production software. While it is used in introductory C++, it pollutes the global namespace with standard library symbols. Be more specific and use "using std::thing;" instead.'
            )

        return lines, True
