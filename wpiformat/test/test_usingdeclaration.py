from wpiformat.usingdeclaration import UsingDeclaration

from .test_tasktest import *


def test_usingdeclaration():
    test = TaskTest(UsingDeclaration())

    # Before class block
    test.add_input(
        "./Test.h",
        """using std::chrono;
class Test {
}
""",
    )
    test.add_verbatim_output(
        "./Test.h: 1: 'using std::chrono;' in global namespace\n", False
    )

    # Inside enum block
    test.add_input(
        "./Test.h",
        """enum Test {
  using std::chrono;
}
""",
    )
    test.add_output("", True)

    # After { block
    test.add_input(
        "./Test.h",
        """{
}
using std::chrono;
""",
    )
    test.add_verbatim_output(
        "./Test.h: 3: 'using std::chrono;' in global namespace\n", False
    )

    # Before class block with NOLINT
    test.add_input(
        "./Test.h",
        """using std::chrono;  // NOLINT
class Test {
}
""",
    )
    test.add_output("", True)

    # "using" in comment without trailing semicolon
    test.add_input(
        "./Test.h",
        """// using
void func() {
  using A = int;
  using B = int;
}
""",
    )
    test.add_output("", True)

    test.run(OutputType.STDOUT)
