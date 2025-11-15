"""This task ensures that the file has zero EOF newlines if it's empty or one EOF newline."""

from wpiformat.config import Config
from wpiformat.task import PipelineTask


class EofNewline(PipelineTask):
    def run_pipeline(
        self, config_file: Config, filename: str, lines: str
    ) -> tuple[str, bool]:
        lines = lines.rstrip()
        if lines:
            return lines + super().get_linesep(lines), True
        else:
            return lines, True
