import os

from wpiformat.config import Config
from wpiformat.includeguard import IncludeGuard


def test_includeguard():
    task = IncludeGuard()

    inputs = []
    outputs = []

    # Fix incorrect include guard
    inputs.append(("./Test.h",
        "#ifndef WRONG_H" + os.linesep + \
        "#define WRONG_C" + os.linesep + \
        os.linesep + \
        "#endif" + os.linesep))
    outputs.append((
        "#ifndef STYLEGUIDE_WPIFORMAT_TEST_H_" + os.linesep + \
        "#define STYLEGUIDE_WPIFORMAT_TEST_H_" + os.linesep + \
        os.linesep + \
        "#endif  // STYLEGUIDE_WPIFORMAT_TEST_H_" + os.linesep, True, True))

    # Ensure nested preprocessor statements are handled properly for incorrect
    # include guard
    inputs.append(("./Test.h",
        "#ifndef WRONG_H" + os.linesep + \
        "#define WRONG_C" + os.linesep + \
        os.linesep + \
        "#if SOMETHING" + os.linesep + \
        "// do something" + os.linesep + \
        "#endif" + os.linesep + \
        "#endif" + os.linesep))
    outputs.append((
        "#ifndef STYLEGUIDE_WPIFORMAT_TEST_H_" + os.linesep + \
        "#define STYLEGUIDE_WPIFORMAT_TEST_H_" + os.linesep + \
        os.linesep + \
        "#if SOMETHING" + os.linesep + \
        "// do something" + os.linesep + \
        "#endif" + os.linesep + \
        "#endif  // STYLEGUIDE_WPIFORMAT_TEST_H_" + os.linesep, True, True))

    # Don't touch correct include guard
    inputs.append(("./Test.h",
        "#ifndef STYLEGUIDE_WPIFORMAT_TEST_H_" + os.linesep + \
        "#define STYLEGUIDE_WPIFORMAT_TEST_H_" + os.linesep + \
        os.linesep + \
        "#endif  // STYLEGUIDE_WPIFORMAT_TEST_H_" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    # Fail on missing include guard
    inputs.append(("./Test.h", "// Empty file" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, False))

    # Verify pragma once counts as include guard
    inputs.append(("./Test.h", "#pragma once" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    assert len(inputs) == len(outputs)

    config_file = Config(os.path.abspath(os.getcwd()), ".styleguide")
    for i in range(len(inputs)):
        output, file_changed, success = task.run_pipeline(
            config_file, inputs[i][0], inputs[i][1])
        assert output == outputs[i][0]
        assert file_changed == outputs[i][1]
        assert success == outputs[i][2]
