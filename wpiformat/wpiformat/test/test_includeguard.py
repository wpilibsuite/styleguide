import os

from .tasktest import *
from .tempdir import *
from wpiformat.includeguard import IncludeGuard
from wpiformat.task import Task


def test_includeguard():
    test = TaskTest(IncludeGuard())

    with OpenTemporaryDirectory():
        with open(".styleguide", "w") as file:
            # Roots are ordered this way to ensure tests find longest match
            file.write(r"""includeGuardRoots {
  wpiformat/
  wpiformat/Test/
}
""")
        repo_root = os.path.basename(Task.get_repo_root()).upper()

        # Fix incorrect include guard
        test.add_input("./Test.h",
            "#ifndef WRONG_H" + os.linesep + \
            "#define WRONG_C" + os.linesep + \
            os.linesep + \
            "#endif" + os.linesep)
        test.add_output(
            "#ifndef " + repo_root + "_TEST_H_" + os.linesep + \
            "#define " + repo_root + "_TEST_H_" + os.linesep + \
            os.linesep + \
            "#endif  // " + repo_root + "_TEST_H_" + os.linesep, True, True)

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
            "#ifndef " + repo_root + "_TEST_H_" + os.linesep + \
            "#define " + repo_root + "_TEST_H_" + os.linesep + \
            os.linesep + \
            "#if SOMETHING" + os.linesep + \
            "// do something" + os.linesep + \
            "#endif" + os.linesep + \
            "#endif  // " + repo_root + "_TEST_H_" + os.linesep, True, True)

        # Don't touch correct include guard
        test.add_input("./Test.h",
            "#ifndef " + repo_root + "_TEST_H_" + os.linesep + \
            "#define " + repo_root + "_TEST_H_" + os.linesep + \
            os.linesep + \
            "#endif  // " + repo_root + "_TEST_H_" + os.linesep)
        test.add_latest_input_as_output(True)

        # Fail on missing include guard
        test.add_input("./Test.h", "// Empty file" + os.linesep)
        test.add_latest_input_as_output(False)

        # Verify pragma once counts as include guard
        test.add_input("./Test.h", "#pragma once" + os.linesep)
        test.add_latest_input_as_output(True)

        # Ensure include guard roots are processed correctly
        test.add_input("./Test.h",
            "#ifndef " + repo_root + "_WPIFORMAT_TEST_H_" + os.linesep + \
            "#define " + repo_root + "_WPIFORMAT_TEST_H_" + os.linesep + \
            os.linesep + \
            "#endif  // " + repo_root + "_WPIFORMAT_TEST_H_" + os.linesep)
        test.add_output(
            "#ifndef " + repo_root + "_TEST_H_" + os.linesep + \
            "#define " + repo_root + "_TEST_H_" + os.linesep + \
            os.linesep + \
            "#endif  // " + repo_root + "_TEST_H_" + os.linesep, True, True)

        # Ensure leading underscores are removed (this occurs if the user doesn't
        # include a trailing "/" in the include guard root)
        test.add_input("./Test/Test.h",
            "#ifndef " + repo_root + "_WPIFORMAT_TEST_TEST_H_" + os.linesep + \
            "#define " + repo_root + "_WPIFORMAT_TEST_TEST_H_" + os.linesep + \
            os.linesep + \
            "#endif  // " + repo_root + "_WPIFORMAT_TEST_TEST_H_" + os.linesep)
        test.add_output(
            "#ifndef " + repo_root + "_TEST_H_" + os.linesep + \
            "#define " + repo_root + "_TEST_H_" + os.linesep + \
            os.linesep + \
            "#endif  // " + repo_root + "_TEST_H_" + os.linesep, True, True)

        test.run(OutputType.FILE)
