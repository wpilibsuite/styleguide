import os

from wpiformat.config import Config
from wpiformat.newline import Newline


def test_newline():
    task = Newline()

    inputs = []
    outputs = []

    file_appendix = \
        "#pragma once" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep + \
        os.linesep + \
        "int main() {" + os.linesep + \
        "  std::cout << \"Hello World!\";" + os.linesep + \
        "}"

    # Empty file
    inputs.append(("./Test.h", ""))
    outputs.append(("\n", True, True))

    # No newline
    inputs.append(("./Test.h", file_appendix))
    outputs.append((file_appendix + os.linesep, True, True))

    # One newline
    inputs.append((inputs[1][0], inputs[1][1] + os.linesep))
    outputs.append((outputs[1][0], False, True))

    # Two newlines
    inputs.append((inputs[1][0], inputs[1][1] + os.linesep + os.linesep))
    outputs.append((outputs[1][0], True, True))

    # .bat file with no "./" prefix
    inputs.append(("test.bat", inputs[1][1].replace(os.linesep, "\r\n")))
    outputs.append((outputs[1][0].replace(os.linesep, "\r\n"), True, True))

    assert len(inputs) == len(outputs)

    config_file = Config(os.path.abspath(os.getcwd()), ".styleguide")
    for i in range(len(inputs)):
        output, file_changed, success = task.run_pipeline(
            config_file, inputs[i][0], inputs[i][1])
        assert output == outputs[i][0]
        assert file_changed == outputs[i][1]
        assert success == outputs[i][2]
