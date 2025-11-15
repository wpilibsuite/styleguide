import os

from wpiformat.eofnewline import EofNewline

from .test_tasktest import *


def test_eofnewline():
    test = TaskTest(EofNewline())

    file_appendix = """#pragma once

#include <iostream>

int main() {
  std::cout << "Hello World!";
}"""

    # Empty file
    test.add_input("./Test.h", "")
    test.add_output("", True)

    test_output = f"{file_appendix}\n"

    # No newline
    test.add_input("./Test.h", file_appendix)
    test.add_output(test_output, True)

    # One newline
    test.add_input("./Test.h", test_output)
    test.add_latest_input_as_output(True)

    # Two newlines
    test.add_input("./Test.h", f"{test_output}\n")
    test.add_output(test_output, True)

    # .bat file with no "./" prefix
    if os.linesep == "\r\n":
        test.add_input("test.bat", file_appendix)
        test.add_output(test_output, True)
    else:
        test.add_input("test.bat", file_appendix.replace("\n", "\r\n"))
        test.add_output(test_output.replace("\n", "\r\n"), True)

    test.run(OutputType.FILE)
