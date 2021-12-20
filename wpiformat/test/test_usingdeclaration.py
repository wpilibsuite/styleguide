from pathlib import Path

from wpiformat.usingdeclaration import UsingDeclaration

from .test_tasktest import *


def test_usingdeclaration():
    test_h = Path("./Test.h").resolve()

    # Before class block
    run_and_check_stdout(
        UsingDeclaration(),
        test_h,
        """using std::chrono;
class Test {
}
""",
        f"warning: {test_h}: 1: 'using std::chrono;' in global namespace\n",
        False,
    )

    # Inside enum block
    run_and_check_stdout(
        UsingDeclaration(),
        test_h,
        """enum Test {
  using std::chrono;
}
""",
        "",
        True,
    )

    # After { block
    run_and_check_stdout(
        UsingDeclaration(),
        test_h,
        """{
}
using std::chrono;
""",
        f"warning: {test_h}: 3: 'using std::chrono;' in global namespace\n",
        False,
    )

    # Before class block with NOLINT
    run_and_check_stdout(
        UsingDeclaration(),
        test_h,
        """using std::chrono;  // NOLINT
class Test {
}
""",
        "",
        True,
    )

    # "using" in comment without trailing semicolon
    run_and_check_stdout(
        UsingDeclaration(),
        test_h,
        """// using
void func() {
  using A = int;
  using B = int;
}
""",
        "",
        True,
    )
