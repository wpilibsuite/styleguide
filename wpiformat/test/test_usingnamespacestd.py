import subprocess
from pathlib import Path

from wpiformat.usingnamespacestd import UsingNamespaceStd

from .test_tasktest import *


def test_usingnamespacestd():
    with OpenTemporaryDirectory():
        subprocess.run(["git", "init", "-q"])
        Path(".wpiformat").write_text(
            r"""cppSrcFileInclude {
  \.cpp$
}
"""
        )

        main_cpp = Path("./Main.cpp").resolve()

        warning_str = 'avoid "using namespace std;" in production software. While it is used in introductory C++, it pollutes the global namespace with standard library symbols. Be more specific and use "using std::thing;" instead.\n'

        # Hello World
        run_and_check_stdout(
            UsingNamespaceStd(),
            main_cpp,
            """using namespace std;

int main() {
  cout << "Hello World!"
}
""",
            f"warning: {main_cpp}: 1: " + warning_str,
            True,
        )

        # Inside braces and not first line
        run_and_check_stdout(
            UsingNamespaceStd(),
            main_cpp,
            """int main() {
  using namespace std;
  cout << "Hello World!"
}
""",
            f"warning: {main_cpp}: 2: " + warning_str,
            True,
        )

        # std::chrono
        run_and_check_stdout(
            UsingNamespaceStd(),
            main_cpp,
            """#include <thread>

int main() {
  using namespace std::chrono;

  std::this_thread::sleep_for(10ms);
}
""",
            f"warning: {main_cpp}: 4: " + warning_str,
            True,
        )

        # Ignore std::literals
        run_and_check_stdout(
            UsingNamespaceStd(), main_cpp, "using namespace std::literals;\n", "", True
        )

        # Ignore std::chrono_literals
        run_and_check_stdout(
            UsingNamespaceStd(),
            main_cpp,
            "using namespace std::chrono_literals;\n",
            "",
            True,
        )

        # Ignore std::string_view_literals
        run_and_check_stdout(
            UsingNamespaceStd(),
            main_cpp,
            "using namespace std::string_view_literals;\n",
            "",
            True,
        )

        # Ignore std::placeholders
        run_and_check_stdout(
            UsingNamespaceStd(),
            main_cpp,
            "using namespace std::placeholders;\n",
            "",
            True,
        )
