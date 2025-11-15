import os

from wpiformat.includeguard import IncludeGuard
from wpiformat.task import Task

from .test_tasktest import *


def test_includeguard():
    test = TaskTest(IncludeGuard())

    repo_root = os.path.basename(Task.get_repo_root()).upper()

    # Fix incorrect include guard
    test.add_input(
        "./Test.h",
        """#ifndef WRONG_H
#define WRONG_C

#endif
""",
    )
    test.add_output(
        f"""#ifndef {repo_root}_TEST_H_
#define {repo_root}_TEST_H_

#endif  // {repo_root}_TEST_H_
""",
        True,
    )

    # Ensure nested preprocessor statements are handled properly for incorrect
    # include guard
    test.add_input(
        "./Test.h",
        """#ifndef WRONG_H
#define WRONG_C

#if SOMETHING
// do something
#endif
#endif
""",
    )
    test.add_output(
        f"""#ifndef {repo_root}_TEST_H_
#define {repo_root}_TEST_H_

#if SOMETHING
// do something
#endif
#endif  // {repo_root}_TEST_H_
""",
        True,
    )

    # Don't touch correct include guard
    test.add_input(
        "./Test.h",
        f"""#ifndef {repo_root}_TEST_H_
#define {repo_root}_TEST_H_

#endif  // {repo_root}_TEST_H_
""",
    )
    test.add_latest_input_as_output(True)

    # Fail on missing include guard
    test.add_input("./Test.h", "// Empty file\n")
    test.add_latest_input_as_output(False)

    # Verify pragma once counts as include guard
    test.add_input("./Test.h", "#pragma once\n")
    test.add_latest_input_as_output(True)

    # Ensure include guard roots are processed correctly
    test.add_input(
        "./Test.h",
        f"""#ifndef {repo_root}_WPIFORMAT_TEST_H_
#define {repo_root}_WPIFORMAT_TEST_H_

#endif  // {repo_root}_WPIFORMAT_TEST_H_
""",
    )
    test.add_output(
        f"""#ifndef {repo_root}_TEST_H_
#define {repo_root}_TEST_H_

#endif  // {repo_root}_TEST_H_
""",
        True,
    )

    # Ensure leading underscores are removed (this occurs if the user doesn't
    # include a trailing "/" in the include guard root)
    test.add_input(
        "./Test/Test.h",
        f"""#ifndef {repo_root}_WPIFORMAT_TEST_TEST_H_
#define {repo_root}_WPIFORMAT_TEST_TEST_H_

#endif  // {repo_root}_WPIFORMAT_TEST_TEST_H_
""",
    )
    test.add_output(
        f"""#ifndef {repo_root}_TEST_H_
#define {repo_root}_TEST_H_

#endif  // {repo_root}_TEST_H_
""",
        True,
    )

    test.run(OutputType.FILE)
