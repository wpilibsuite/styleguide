"""This task runs clang-tidy on the file."""

import subprocess
import sys

from wpiformat.task import Task


class ClangTidy(Task):
    def __init__(self, clang_version, compile_commands, extra_args):
        """Constructor for ClangTidy task.

        Keyword arguments:
        clang_version -- version number of clang-tidy appended to executable
                         name
        compile_commands -- directory containing compile_commands.json
        extra_args -- list of extra arguments to clang-tidy
        """
        super().__init__()

        if clang_version == "":
            self.exec_name = "clang-tidy"
        else:
            self.exec_name = "clang-tidy-" + clang_version

        self.args = ["--quiet"]
        if compile_commands:
            self.args += ["-p", compile_commands]

        # Prepend a dash to the argument here because the main argument parser
        # treats strings with a dash prefix as a new argument instead of the
        # value for -extra-args
        for arg in extra_args:
            self.args += ["-extra-arg", "-" + arg]

    @staticmethod
    def should_process_file(config_file, name):
        return config_file.is_cpp_file(name)

    def run_standalone(self, config_file, name):
        try:
            output = subprocess.run(
                [self.exec_name] + self.args + [name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
            ).stdout
        except FileNotFoundError:
            print(
                "Error: " + self.exec_name + " not found in PATH. Is it installed?",
                file=sys.stderr,
            )
            return False

        lines = [l for l in output.rstrip().split("\n") if l]

        # Filter out "X error(s) and Y warning(s) generated." lines
        lines = [l for l in lines if " generated." not in l]

        # Filter out "Error while processing" lines
        lines = [l for l in lines if "Error while processing" not in l]

        # Ignore include file not found errors
        filtered_lines = []
        iterlines = iter(lines)
        for l in iterlines:
            if "file not found [clang-diagnostic-error]" in l:
                # Skip #include line and caret indicator line
                next(iterlines)
                next(iterlines)
            else:
                filtered_lines.append(l)
        lines = filtered_lines

        if lines:
            print(f"== clang-tidy {name} ==\n" + "\n".join(lines))
            return False

        return True
