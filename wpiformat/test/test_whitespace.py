from wpiformat.whitespace import Whitespace

from .test_tasktest import *


def test_whitespace():
    test = TaskTest(Whitespace())

    file_appendix = """#pragma once

#include <iostream>

int main() {
  std::cout << "Hello World!";
}
"""

    # Empty file
    test.add_input("./Test.h", "")
    test.add_output("", True)

    # No trailing whitespace
    test.add_input("./Test.h", file_appendix)
    test.add_output(file_appendix, True)

    # Two spaces trailing
    test.add_input(
        "./Test.h",
        "#pragma once\n"
        + "\n"
        + "#include <iostream>\n"
        + "\n"
        + "int main() {  \n"
        + '  std::cout << "Hello World!";  \n'
        + "}\n",
    )
    test.add_output(file_appendix, True)

    # Two tabs trailing
    test.add_input(
        "./Test.h",
        """#pragma once

#include <iostream>

int main() {\t\t
  std::cout << "Hello World!";\t\t
}
""",
    )
    test.add_output(file_appendix, True)

    test.run(OutputType.FILE)
