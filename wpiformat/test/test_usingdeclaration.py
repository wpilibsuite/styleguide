import subprocess
from pathlib import Path

from wpiformat.usingdeclaration import UsingDeclaration

from .test_tasktest import *


def test_usingdeclaration():
    with OpenTemporaryDirectory():
        subprocess.run(["git", "init", "-q"])

        test_hpp = Path("./Test.hpp").resolve()

        # Before class block
        run_and_check_stdout(
            UsingDeclaration(),
            test_hpp,
            """using std::chrono;
class Test {
}
""",
            f"warning: {test_hpp}: 1: 'using std::chrono;' in global namespace\n",
            False,
        )

        # Inside enum block
        run_and_check_stdout(
            UsingDeclaration(),
            test_hpp,
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
            test_hpp,
            """{
}
using std::chrono;
""",
            f"warning: {test_hpp}: 3: 'using std::chrono;' in global namespace\n",
            False,
        )

        # Before class block with NOLINT
        run_and_check_stdout(
            UsingDeclaration(),
            test_hpp,
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
            test_hpp,
            """// using
void func() {
  using A = int;
  using B = int;
}
""",
            "",
            True,
        )
