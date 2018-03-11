import os

from test.tasktest import *
from wpiformat.includeguard import IncludeGuard


def test_includeguard():
    test = TaskTest(IncludeGuard())

    # Fix incorrect include guard
    test.add_input("./Test.h",
        "#ifndef WRONG_H" + os.linesep + \
        "#define WRONG_C" + os.linesep + \
        os.linesep + \
        "#endif" + os.linesep)
    test.add_output(
        "#ifndef STYLEGUIDE_TEST_H_" + os.linesep + \
        "#define STYLEGUIDE_TEST_H_" + os.linesep + \
        os.linesep + \
        "#endif  // STYLEGUIDE_TEST_H_" + os.linesep, True, True)

    # Ensure nested preprocessor statements are handled properly for incorrect
    # include guard
    test.add_input("./Test.h",
        "#ifndef WRONG_H" + os.linesep + \
        "#define WRONG_C" + os.linesep + \
        os.linesep + \
        "#if SOMETHING" + os.linesep + \
        "// do something" + os.linesep + \
        "#endif" + os.linesep + \
        "#endif" + os.linesep)
    test.add_output(
        "#ifndef STYLEGUIDE_TEST_H_" + os.linesep + \
        "#define STYLEGUIDE_TEST_H_" + os.linesep + \
        os.linesep + \
        "#if SOMETHING" + os.linesep + \
        "// do something" + os.linesep + \
        "#endif" + os.linesep + \
        "#endif  // STYLEGUIDE_TEST_H_" + os.linesep, True, True)

    # Don't touch correct include guard
    test.add_input("./Test.h",
        "#ifndef STYLEGUIDE_TEST_H_" + os.linesep + \
        "#define STYLEGUIDE_TEST_H_" + os.linesep + \
        os.linesep + \
        "#endif  // STYLEGUIDE_TEST_H_" + os.linesep)
    test.add_latest_input_as_output(True)

    # Fail on missing include guard
    test.add_input("./Test.h", "// Empty file" + os.linesep)
    test.add_latest_input_as_output(False)

    # Verify pragma once counts as include guard
    test.add_input("./Test.h", "#pragma once" + os.linesep)
    test.add_latest_input_as_output(True)

    # Ensure include guard roots are processed correctly
    test.add_input("./Test.h",
        "#ifndef STYLEGUIDE_WPIFORMAT_TEST_H_" + os.linesep + \
        "#define STYLEGUIDE_WPIFORMAT_TEST_H_" + os.linesep + \
        os.linesep + \
        "#endif  // STYLEGUIDE_WPIFORMAT_TEST_H_" + os.linesep)
    test.add_output(
        "#ifndef STYLEGUIDE_TEST_H_" + os.linesep + \
        "#define STYLEGUIDE_TEST_H_" + os.linesep + \
        os.linesep + \
        "#endif  // STYLEGUIDE_TEST_H_" + os.linesep, True, True)

    test.run(OutputType.FILE)
