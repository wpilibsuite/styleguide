import os

from wpiformat.includeguard import IncludeGuard
from wpiformat.task import Task

from .test_tasktest import *


def test_includeguard():
    repo_root = os.path.basename(Task.get_repo_root()).upper()

    # Fix incorrect include guard
    run_and_check_file(
        IncludeGuard(),
        "./Test.h",
        """#ifndef WRONG_H
#define WRONG_C

#endif
""",
        f"""#ifndef {repo_root}_TEST_H_
#define {repo_root}_TEST_H_

#endif  // {repo_root}_TEST_H_
""",
        True,
    )

    # Ensure nested preprocessor statements are handled properly for incorrect
    # include guard
    run_and_check_file(
        IncludeGuard(),
        "./Test.h",
        """#ifndef WRONG_H
#define WRONG_C

#if SOMETHING
// do something
#endif
#endif
""",
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
    contents = f"""#ifndef {repo_root}_TEST_H_
#define {repo_root}_TEST_H_

#endif  // {repo_root}_TEST_H_
"""
    run_and_check_file(IncludeGuard(), "./Test.h", contents, contents, True)

    # Fail on missing include guard
    run_and_check_file(
        IncludeGuard(), "./Test.h", "// Empty file\n", "// Empty file\n", False
    )

    # Verify pragma once counts as include guard
    run_and_check_file(
        IncludeGuard(), "./Test.h", "#pragma once\n", "#pragma once\n", True
    )

    # Ensure include guard roots are processed correctly
    run_and_check_file(
        IncludeGuard(),
        "./Test.h",
        f"""#ifndef {repo_root}_WPIFORMAT_TEST_H_
#define {repo_root}_WPIFORMAT_TEST_H_

#endif  // {repo_root}_WPIFORMAT_TEST_H_
""",
        f"""#ifndef {repo_root}_TEST_H_
#define {repo_root}_TEST_H_

#endif  // {repo_root}_TEST_H_
""",
        True,
    )

    # Ensure leading underscores are removed (this occurs if the user doesn't
    # include a trailing "/" in the include guard root)
    run_and_check_file(
        IncludeGuard(),
        "./Test/Test.h",
        f"""#ifndef {repo_root}_WPIFORMAT_TEST_TEST_H_
#define {repo_root}_WPIFORMAT_TEST_TEST_H_

#endif  // {repo_root}_WPIFORMAT_TEST_TEST_H_
""",
        f"""#ifndef {repo_root}_TEST_H_
#define {repo_root}_TEST_H_

#endif  // {repo_root}_TEST_H_
""",
        True,
    )
