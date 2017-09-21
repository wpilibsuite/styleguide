import io
import os
import sys

from wpiformat.config import Config
from wpiformat.usingdeclaration import UsingDeclaration


def test_usingdeclaration():
    task = UsingDeclaration()

    inputs = []
    outputs = []

    # Before class block
    inputs.append(("./Test.h",
        "using std::chrono;" + os.linesep + \
        "class Test {" + os.linesep + \
        "}" + os.linesep))
    outputs.append(("./Test.h: 1: 'using std::chrono;' in global namespace\n",
                    False, False))

    # Inside enum block
    inputs.append(("./Test.h",
        "enum Test {" + os.linesep + \
        "  using std::chrono;" + os.linesep + \
        "}" + os.linesep))
    outputs.append(("", False, True))

    # After { block
    inputs.append(("./Test.h",
        "{" + os.linesep + \
        "}" + os.linesep + \
        "using std::chrono;" + os.linesep))
    outputs.append(("./Test.h: 3: 'using std::chrono;' in global namespace\n",
                    False, False))

    # Before class block with NOLINT
    inputs.append(("./Test.h",
        "using std::chrono;  // NOLINT" + os.linesep + \
        "class Test {" + os.linesep + \
        "}" + os.linesep))
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
        assert output == outputs[i][0]
        assert file_changed == outputs[i][1]
        assert success == outputs[i][2]
