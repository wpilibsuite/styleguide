import os

from wpiformat.config import Config
from wpiformat.whitespace import Whitespace


def test_whitespace():
    task = Whitespace()

    inputs = []
    outputs = []

    file_appendix = \
        "#pragma once" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep + \
        os.linesep + \
        "int main() {" + os.linesep + \
        "  std::cout << \"Hello World!\";" + os.linesep + \
        "}" + os.linesep

    # Empty file
    inputs.append(("./Test.h", ""))
    outputs.append(("", False, True))

    # No trailing whitespace
    inputs.append(("./Test.h", file_appendix))
    outputs.append((file_appendix, False, True))

    # Two spaces trailing
    inputs.append(
        ("./Test.h",
         "#pragma once" + os.linesep + os.linesep + "#include <iostream>" +
         os.linesep + os.linesep + "int main() {  " + os.linesep +
         "  std::cout << \"Hello World!\";  " + os.linesep + "}" + os.linesep))
    outputs.append((file_appendix, True, True))

    # Two tabs trailing
    inputs.append((
        "./Test.h",
        "#pragma once" + os.linesep + os.linesep + "#include <iostream>" +
        os.linesep + os.linesep + "int main() {\t\t" + os.linesep +
        "  std::cout << \"Hello World!\";\t\t" + os.linesep + "}" + os.linesep))
    outputs.append((file_appendix, True, True))

    assert len(inputs) == len(outputs)

    config_file = Config(os.path.abspath(os.getcwd()), ".styleguide")
    for i in range(len(inputs)):
        output, file_changed, success = task.run_pipeline(
            config_file, inputs[i][0], inputs[i][1])
        assert output == outputs[i][0]
        assert file_changed == outputs[i][1]
        assert success == outputs[i][2]
