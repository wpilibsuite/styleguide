import os

from .test_tasktest import *
from wpiformat.eofnewline import EofNewline


def test_eofnewline():
    test = TaskTest(EofNewline())

    file_appendix = (
        "#pragma once"
        + os.linesep
        + os.linesep
        + "#include <iostream>"
        + os.linesep
        + os.linesep
        + "int main() {"
        + os.linesep
        + '  std::cout << "Hello World!";'
        + os.linesep
        + "}"
    )

    # Empty file
    test.add_input("./Test.h", "")
    test.add_output("\n", True)

    test_output = file_appendix + os.linesep

    # No newline
    test.add_input("./Test.h", file_appendix)
    test.add_output(test_output, True)

    # One newline
    test.add_input("./Test.h", test_output)
    test.add_latest_input_as_output(True)

    # Two newlines
    test.add_input("./Test.h", test_output + os.linesep)
    test.add_output(test_output, True)

    # .bat file with no "./" prefix
    test.add_input("test.bat", file_appendix.replace(os.linesep, "\r\n"))
    test.add_output(test_output.replace(os.linesep, "\r\n"), True)

    test.run(OutputType.FILE)
