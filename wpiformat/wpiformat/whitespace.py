"""This task removes trailing whitespace from the file."""

from pathlib import Path

from wpiformat.config import Config
from wpiformat.task import PipelineTask


class Whitespace(PipelineTask):
    def run_pipeline(
        self, config_file: Config, filename: Path, lines: str
    ) -> tuple[str, bool]:
        linesep = super().get_linesep(lines)

        return "".join(line.rstrip() + linesep for line in lines.splitlines()), True
