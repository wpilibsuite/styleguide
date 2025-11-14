from wpiformat.usingnamespacestd import UsingNamespaceStd

from .test_tasktest import *


def test_usingnamespacestd():
    test = TaskTest(UsingNamespaceStd())

    warning_str = 'avoid "using namespace std;" in production software. While it is used in introductory C++, it pollutes the global namespace with standard library symbols. Be more specific and use "using std::thing;" instead.\n'

    # Hello World
    test.add_input(
        "./Main.cpp",
        """using namespace std;

int main() {
  cout << "Hello World!"
}
""",
    )
    test.add_verbatim_output("warning: ./Main.cpp: 1: " + warning_str, True)

    # Inside braces and not first line
    test.add_input(
        "./Main.cpp",
        """int main() {
  using namespace std;
  cout << "Hello World!"
}
""",
    )
    test.add_verbatim_output("warning: ./Main.cpp: 2: " + warning_str, True)

    # std::chrono
    test.add_input(
        "./Main.cpp",
        """#include <thread>

int main() {
  using namespace std::chrono;

  std::this_thread::sleep_for(10ms);
}
""",
    )
    test.add_verbatim_output("warning: ./Main.cpp: 4: " + warning_str, True)

    # Ignore std::literals
    test.add_input("./Main.cpp", "using namespace std::literals;\n")
    test.add_output("", True)

    # Ignore std::chrono_literals
    test.add_input("./Main.cpp", "using namespace std::chrono_literals;\n")
    test.add_output("", True)

    # Ignore std::string_view_literals
    test.add_input("./Main.cpp", "using namespace std::string_view_literals;\n")
    test.add_output("", True)

    # Ignore std::placeholders
    test.add_input("./Main.cpp", "using namespace std::placeholders;\n")
    test.add_output("", True)

    test.run(OutputType.STDOUT)
