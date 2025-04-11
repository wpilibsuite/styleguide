"""This task ensures that the file has zero EOF newlines if it's empty or one EOF newline."""

from wpiformat.task import PipelineTask


class EofNewline(PipelineTask):
    def run_pipeline(self, config_file, name, lines):
        lines = lines.rstrip()
        if lines:
            return lines + super().get_linesep(lines), True
        else:
            return lines, True
