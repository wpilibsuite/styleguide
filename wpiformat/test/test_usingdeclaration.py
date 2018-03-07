import io
import os
import sys

from test.tasktest import *
from wpiformat.usingdeclaration import UsingDeclaration


def test_usingdeclaration():
    test = TaskTest(UsingDeclaration())

    # Before class block
    test.add_input("./Test.h",
        "using std::chrono;" + os.linesep + \
        "class Test {" + os.linesep + \
        "}" + os.linesep)
    test.add_output("./Test.h: 1: 'using std::chrono;' in global namespace\n",
                    False, False)

    # Inside enum block
    test.add_input("./Test.h",
        "enum Test {" + os.linesep + \
        "  using std::chrono;" + os.linesep + \
        "}" + os.linesep)
    test.add_output("", False, True)

    # After { block
    test.add_input("./Test.h",
        "{" + os.linesep + \
        "}" + os.linesep + \
        "using std::chrono;" + os.linesep)
    test.add_output("./Test.h: 3: 'using std::chrono;' in global namespace\n",
                    False, False)

    # Before class block with NOLINT
    test.add_input("./Test.h",
        "using std::chrono;  // NOLINT" + os.linesep + \
        "class Test {" + os.linesep + \
        "}" + os.linesep)
    test.add_output("", False, True)

    test.run(OutputType.STDOUT)
