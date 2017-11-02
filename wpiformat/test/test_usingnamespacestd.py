import io
import os
import sys

from wpiformat.config import Config
from wpiformat.usingnamespacestd import UsingNamespaceStd


def test_usingnamespacestd():
    task = UsingNamespaceStd()

    inputs = []
    outputs = []

    warning_str = "avoid \"using namespace std;\" in production software. While it is used in introductory C++, it pollutes the global namespace with standard library symbols.\n"

    # Hello World
    inputs.append(("./Main.cpp",
        "using namespace std;" + os.linesep + \
        os.linesep + \
        "int main() {" + os.linesep + \
        "  cout << \"Hello World!\"" + os.linesep + \
        "}" + os.linesep))
    outputs.append(("Warning: ./Main.cpp: 1: " + warning_str, False, True))

    # Inside braces and not first line
    inputs.append(("./Main.cpp",
        "int main() {" + os.linesep + \
        "  using namespace std;" + os.linesep + \
        "  cout << \"Hello World!\"" + os.linesep + \
        "}" + os.linesep))
    outputs.append(("Warning: ./Main.cpp: 2: " + warning_str, False, True))

    # std::chrono
    inputs.append(("./Main.cpp",
        "#include <thread>" + os.linesep + \
        os.linesep + \
        "int main() {" + os.linesep + \
        "  using namespace std::chrono;" + os.linesep + \
        os.linesep + \
        "  std::this_thread::sleep_for(10ms);" + os.linesep + \
        "}" + os.linesep))
    outputs.append(("Warning: ./Main.cpp: 4: " + warning_str, False, True))

    # Ignore std::literals
    inputs.append(("./Main.cpp", "using namespace std::literals;" + os.linesep))
    outputs.append(("", False, True))

    # Ignore std::chrono_literals
    inputs.append(("./Main.cpp",
                   "using namespace std::chrono_literals;" + os.linesep))
    outputs.append(("", False, True))

    assert len(inputs) == len(outputs)

    config_file = Config(os.path.abspath(os.getcwd()), ".styleguide")
    saved_stdout = sys.stdout
    for i in range(len(inputs)):
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        unused_output, file_changed, success = task.run_pipeline(
            config_file, inputs[i][0], inputs[i][1])
        sys.stdout = saved_stdout
        new_stdout.seek(0)
        output = new_stdout.read()
        print("Running test {}...".format(i))
        print("output=", output)
        print("outputs[i][0]=", outputs[i][0])
        assert output == outputs[i][0]
        assert file_changed == outputs[i][1]
        assert success == outputs[i][2]
