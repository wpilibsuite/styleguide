from wpiformat.whitespace import Whitespace

from .test_tasktest import *


def test_whitespace():
    file_appendix = """#pragma once

#include <iostream>

int main() {
  std::cout << "Hello World!";
}
"""

    # Empty file
    run_and_check_file(Whitespace(), "./Test.h", "", "", True)

    # No trailing whitespace
    run_and_check_file(Whitespace(), "./Test.h", file_appendix, file_appendix, True)

    # Two spaces trailing
    run_and_check_file(
        Whitespace(),
        "./Test.h",
        "#pragma once\n"
        + "\n"
        + "#include <iostream>\n"
        + "\n"
        + "int main() {  \n"
        + '  std::cout << "Hello World!";  \n'
        + "}\n",
        file_appendix,
        True,
    )

    # Two tabs trailing
    run_and_check_file(
        Whitespace(),
        "./Test.h",
        """#pragma once

#include <iostream>

int main() {\t\t
  std::cout << "Hello World!";\t\t
}
""",
        file_appendix,
        True,
    )
