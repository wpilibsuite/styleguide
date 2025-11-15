"""This class is for writing unit tests for tasks."""

import io
import os
import sys
from enum import Enum

from wpiformat.config import Config
from wpiformat.task import Task


class OutputType(Enum):
    FILE = 1
    STDOUT = 2


class TaskTest:
    def __init__(self, task: Task):
        """Constructor for Test object.

        Keyword arguments:
        task -- task on which to run tests
        """
        self.task = task
        self.inputs = []
        self.outputs = []

    def reset(self):
        """Clears input and output lists."""
        self.inputs = []
        self.outputs = []

    def add_input(self, filename: str, contents: str):
        """Adds the given file and its contents to the input list.

        Keyword arguments:
        filename -- filename
        contents -- file contents
        """
        self.inputs.append((filename, contents.replace("\n", os.linesep)))

    def add_output(self, contents: str, succeeded: bool):
        """Adds the given file contents and whether processing of the input list
        was successful.

        Keyword arguments:
        contents -- file contents
        succeeded -- whether processing of the input list was successful
        """
        self.outputs.append((contents.replace("\n", os.linesep), succeeded))

    def add_verbatim_output(self, contents: str, succeeded: bool):
        """Adds the given file contents and whether processing of the input list
        was successful, without replacing the line separator.

        Keyword arguments:
        contents -- file contents
        succeeded -- whether processing of the input list was successful
        """
        self.outputs.append((contents, succeeded))

    def add_latest_input_as_output(self, succeeded: bool):
        """Adds the latest input to the output list.

        Keyword arguments:
        succeeded -- whether processing of the input list was successful
        """
        self.outputs.append((self.inputs[-1][1], succeeded))

    def run(self, output_type: OutputType):
        """Runs the task on each input list element, then compares the resulting
        output against the corresponding output list element.

        output_type == FILE: output list contains file contents
        output_type == STDOUT: output list contains stdout contents

        Keyword Arguments:
        output_type -- the type of output stored in the output list
        """
        assert len(self.inputs) == len(self.outputs)

        config_file = Config(os.path.abspath(os.getcwd()), ".styleguide")

        for i in range(len(self.inputs)):
            if self.task.should_process_file(config_file, self.inputs[i][0]):
                print("Running test {}...".format(i))

                if output_type == OutputType.FILE:
                    output, success = self.task.run_pipeline(
                        config_file, self.inputs[i][0], self.inputs[i][1]
                    )
                elif output_type == OutputType.STDOUT:
                    saved_stdout = sys.stdout
                    sys.stdout = io.StringIO()
                    _output, success = self.task.run_pipeline(
                        config_file, self.inputs[i][0], self.inputs[i][1]
                    )
                    sys.stdout.seek(0)
                    output = sys.stdout.read()
                    sys.stdout = saved_stdout
            else:
                output = self.inputs[i][1]
                success = True

            assert output == self.outputs[i][0]
            assert success == self.outputs[i][1]
