import subprocess
from pathlib import Path

from wpiformat.includeguard import IncludeGuard
from wpiformat.task import Task

from .test_tasktest import *


def test_includeguard():
    with OpenTemporaryDirectory():
        subprocess.run(["git", "init", "-q"])
        Path(".wpiformat").write_text(
            r"""includeGuardRoots {
  test/
}
"""
        )

        test_hpp = Path("./Test.hpp").resolve()
        test_test_hpp = Path("./test/Test.hpp").resolve()

        repo_root = Task.get_repo_root().name.upper()

        # Fix incorrect include guard
        run_and_check_file(
            IncludeGuard(),
            test_hpp,
            """#ifndef WRONG_H
#define WRONG_C

#endif
""",
            f"""#ifndef {repo_root}_TEST_HPP_
#define {repo_root}_TEST_HPP_

#endif  // {repo_root}_TEST_HPP_
""",
            True,
        )

        # Ensure nested preprocessor statements are handled properly for incorrect
        # include guard
        run_and_check_file(
            IncludeGuard(),
            test_hpp,
            """#ifndef WRONG_H
#define WRONG_C

#if SOMETHING
// do something
#endif
#endif
""",
            f"""#ifndef {repo_root}_TEST_HPP_
#define {repo_root}_TEST_HPP_

#if SOMETHING
// do something
#endif
#endif  // {repo_root}_TEST_HPP_
""",
            True,
        )

        # Don't touch correct include guard
        contents = f"""#ifndef {repo_root}_TEST_HPP_
#define {repo_root}_TEST_HPP_

#endif  // {repo_root}_TEST_HPP_
"""
        run_and_check_file(IncludeGuard(), test_hpp, contents, contents, True)

        # Fail on missing include guard
        run_and_check_file(
            IncludeGuard(), test_hpp, "// Empty file\n", "// Empty file\n", False
        )

        # Verify pragma once counts as include guard
        run_and_check_file(
            IncludeGuard(), test_hpp, "#pragma once\n", "#pragma once\n", True
        )

        # Ensure include guard roots are processed correctly
        run_and_check_file(
            IncludeGuard(),
            test_hpp,
            f"""#ifndef {repo_root}_WPIFORMAT_TEST_HPP_
#define {repo_root}_WPIFORMAT_TEST_HPP_

#endif  // {repo_root}_WPIFORMAT_TEST_HPP_
""",
            f"""#ifndef {repo_root}_TEST_HPP_
#define {repo_root}_TEST_HPP_

#endif  // {repo_root}_TEST_HPP_
""",
            True,
        )

        # Ensure leading underscores are removed (this occurs if the user doesn't
        # include a trailing "/" in the include guard root)
        run_and_check_file(
            IncludeGuard(),
            test_test_hpp,
            f"""#ifndef {repo_root}_WPIFORMAT_TEST_TEST_HPP_
#define {repo_root}_WPIFORMAT_TEST_TEST_HPP_

#endif  // {repo_root}_WPIFORMAT_TEST_TEST_HPP_
""",
            f"""#ifndef {repo_root}_TEST_HPP_
#define {repo_root}_TEST_HPP_

#endif  // {repo_root}_TEST_HPP_
""",
            True,
        )
