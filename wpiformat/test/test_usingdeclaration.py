from wpiformat.usingdeclaration import UsingDeclaration

from .test_tasktest import *


def test_usingdeclaration():
    # Before class block
    run_and_check_stdout(
        UsingDeclaration(),
        "./Test.h",
        """using std::chrono;
class Test {
}
""",
        "warning: ./Test.h: 1: 'using std::chrono;' in global namespace\n",
        False,
    )

    # Inside enum block
    run_and_check_stdout(
        UsingDeclaration(),
        "./Test.h",
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
        "./Test.h",
        """{
}
using std::chrono;
""",
        "warning: ./Test.h: 3: 'using std::chrono;' in global namespace\n",
        False,
    )

    # Before class block with NOLINT
    run_and_check_stdout(
        UsingDeclaration(),
        "./Test.h",
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
        "./Test.h",
        """// using
void func() {
  using A = int;
  using B = int;
}
""",
        "",
        True,
    )
