import io
import os
import sys

from .test_tasktest import *
from wpiformat.usingdeclaration import UsingDeclaration


def test_usingdeclaration():
    test = TaskTest(UsingDeclaration())

    # Before class block
    test.add_input(
        "./Test.h",
        "using std::chrono;"
        + os.linesep
        + "class Test {"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output("./Test.h: 1: 'using std::chrono;' in global namespace\n", False)

    # Inside enum block
    test.add_input(
        "./Test.h",
        "enum Test {"
        + os.linesep
        + "  using std::chrono;"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output("", True)

    # After { block
    test.add_input(
        "./Test.h",
        "{" + os.linesep + "}" + os.linesep + "using std::chrono;" + os.linesep,
    )
    test.add_output("./Test.h: 3: 'using std::chrono;' in global namespace\n", False)

    # Before class block with NOLINT
    test.add_input(
        "./Test.h",
        "using std::chrono;  // NOLINT"
        + os.linesep
        + "class Test {"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output("", True)

    # "using" in comment without trailing semicolon
    test.add_input(
        "./Test.h",
        "// using"
        + os.linesep
        + "void func() {"
        + os.linesep
        + "  using A = int;"
        + os.linesep
        + "  using B = int;"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output("", True)

    test.run(OutputType.STDOUT)
