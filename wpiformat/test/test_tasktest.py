"""This class is for writing unit tests for tasks."""

import io
import os
from contextlib import redirect_stdout

from wpiformat.config import Config
from wpiformat.task import Task


def run_and_check_file(
    task: Task,
    filename: str,
    input_contents: str,
    expected_output_contents: str,
    expected_success: bool,
):
    """
    Runs the task on the input file contents, then compares the resulting output
    against the expected output file contents.

    Keyword Arguments:
    task -- Task instance to test
    filename -- filename
    input_contents -- input file contents
    expected_output_contents -- expected output file contents
    expected_success -- whether run is expected to succeed
    """
    input_contents = input_contents.replace("\n", os.linesep)
    expected_output_contents = expected_output_contents.replace("\n", os.linesep)

    config_file = Config(os.path.abspath(os.getcwd()), ".wpiformat")

    if task.should_process_file(config_file, filename):
        output, success = task.run_pipeline(config_file, filename, input_contents)
    else:
        output = input_contents
        success = True

    assert output == expected_output_contents
    assert success == expected_success


def run_and_check_stdout(
    task: Task,
    filename: str,
    input_contents: str,
    expected_output_contents: str,
    expected_success: bool,
):
    """
    Runs the task on the input file contents, then compares the resulting
    output against the expected stdout contents.

    Keyword Arguments:
    task -- Task instance to test
    filename -- filename
    input_contents -- input file contents
    expected_output_contents -- expected output file contents
    expected_success -- whether run is expected to succeed
    """
    config_file = Config(os.path.abspath(os.getcwd()), ".wpiformat")

    if task.should_process_file(config_file, filename):
        with redirect_stdout(io.StringIO()) as f:
            _, success = task.run_pipeline(config_file, filename, input_contents)
        output = f.getvalue()
    else:
        output = input_contents
        success = True

    assert output == expected_output_contents
    assert success == expected_success
