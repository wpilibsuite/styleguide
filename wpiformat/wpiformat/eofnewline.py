"""This task ensures that the file has exactly one EOF newline."""

from wpiformat.task import PipelineTask


class EofNewline(PipelineTask):
    def run_pipeline(self, config_file, name, lines):
        return lines.rstrip() + super().get_linesep(lines), True
