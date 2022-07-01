import os

from .test_tasktest import *
from wpiformat.usingnamespacestd import UsingNamespaceStd


def test_usingnamespacestd():
    test = TaskTest(UsingNamespaceStd())

    warning_str = 'avoid "using namespace std;" in production software. While it is used in introductory C++, it pollutes the global namespace with standard library symbols. Be more specific and use "using std::thing;" instead.\n'

    # Hello World
    test.add_input(
        "./Main.cpp",
        "using namespace std;"
        + os.linesep
        + os.linesep
        + "int main() {"
        + os.linesep
        + '  cout << "Hello World!"'
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output("Warning: ./Main.cpp: 1: " + warning_str, True)

    # Inside braces and not first line
    test.add_input(
        "./Main.cpp",
        "int main() {"
        + os.linesep
        + "  using namespace std;"
        + os.linesep
        + '  cout << "Hello World!"'
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output("Warning: ./Main.cpp: 2: " + warning_str, True)

    # std::chrono
    test.add_input(
        "./Main.cpp",
        "#include <thread>"
        + os.linesep
        + os.linesep
        + "int main() {"
        + os.linesep
        + "  using namespace std::chrono;"
        + os.linesep
        + os.linesep
        + "  std::this_thread::sleep_for(10ms);"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output("Warning: ./Main.cpp: 4: " + warning_str, True)

    # Ignore std::literals
    test.add_input("./Main.cpp", "using namespace std::literals;" + os.linesep)
    test.add_output("", True)

    # Ignore std::chrono_literals
    test.add_input("./Main.cpp", "using namespace std::chrono_literals;" + os.linesep)
    test.add_output("", True)

    # Ignore std::string_view_literals
    test.add_input(
        "./Main.cpp", "using namespace std::string_view_literals;" + os.linesep
    )
    test.add_output("", True)

    # Ignore std::placeholders
    test.add_input("./Main.cpp", "using namespace std::placeholders;" + os.linesep)
    test.add_output("", True)

    test.run(OutputType.STDOUT)
