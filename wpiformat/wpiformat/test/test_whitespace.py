import os

from .test_tasktest import *
from wpiformat.whitespace import Whitespace


def test_whitespace():
    test = TaskTest(Whitespace())

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
        + os.linesep
    )

    # Empty file
    test.add_input("./Test.h", "")
    test.add_output("", True)

    # No trailing whitespace
    test.add_input("./Test.h", file_appendix)
    test.add_output(file_appendix, True)

    # Two spaces trailing
    test.add_input(
        "./Test.h",
        "#pragma once"
        + os.linesep
        + os.linesep
        + "#include <iostream>"
        + os.linesep
        + os.linesep
        + "int main() {  "
        + os.linesep
        + '  std::cout << "Hello World!";  '
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output(file_appendix, True)

    # Two tabs trailing
    test.add_input(
        "./Test.h",
        "#pragma once"
        + os.linesep
        + os.linesep
        + "#include <iostream>"
        + os.linesep
        + os.linesep
        + "int main() {\t\t"
        + os.linesep
        + '  std::cout << "Hello World!";\t\t'
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output(file_appendix, True)

    test.run(OutputType.FILE)
