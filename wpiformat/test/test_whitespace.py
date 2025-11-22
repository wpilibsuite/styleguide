import subprocess
from pathlib import Path

from wpiformat.whitespace import Whitespace

from .test_tasktest import *


def test_whitespace():
    with OpenTemporaryDirectory():
        subprocess.run(["git", "init", "-q"])

        test_hpp = Path("./Test.hpp").resolve()

        file_appendix = """#pragma once

#include <iostream>

int main() {
  std::cout << "Hello World!";
}
"""

        # Empty file
        run_and_check_file(Whitespace(), test_hpp, "", "", True)

        # No trailing whitespace
        run_and_check_file(Whitespace(), test_hpp, file_appendix, file_appendix, True)

        # Two spaces trailing
        run_and_check_file(
            Whitespace(),
            test_hpp,
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
            test_hpp,
            """#pragma once

#include <iostream>

int main() {\t\t
  std::cout << "Hello World!";\t\t
}
""",
            file_appendix,
            True,
        )
