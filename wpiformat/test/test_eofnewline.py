import os

from wpiformat.eofnewline import EofNewline

from .test_tasktest import *


def test_eofnewline():
    file_appendix = """#pragma once

#include <iostream>

int main() {
  std::cout << "Hello World!";
}"""
    test_output = f"{file_appendix}\n"

    # Empty file
    run_and_check_file(EofNewline(), "./Test.h", "", "", True)

    # No newline
    run_and_check_file(EofNewline(), "./Test.h", file_appendix, test_output, True)

    # One newline
    run_and_check_file(EofNewline(), "./Test.h", test_output, test_output, True)

    # Two newlines
    run_and_check_file(EofNewline(), "./Test.h", f"{test_output}\n", test_output, True)

    # .bat file with no "./" prefix
    if os.linesep == "\r\n":
        run_and_check_file(EofNewline(), "test.bat", file_appendix, test_output, True)
    else:
        run_and_check_file(
            EofNewline(),
            "test.bat",
            file_appendix.replace("\n", "\r\n"),
            test_output.replace("\n", "\r\n"),
            True,
        )
