import os

from wpiformat.config import Config
from wpiformat.bracecomment import BraceComment


def test_bracecomment():
    task = BraceComment()

    inputs = []
    outputs = []

    # Empty anonymous namespace
    inputs.append(("./Test.h",
        "namespace {" + os.linesep + \
        "}// comment" + os.linesep))
    outputs.append((
        "namespace {" + os.linesep + \
        "}  // namespace" + os.linesep, True, True))

    # Anonymous namespace containing comment
    inputs.append(("./Test.h",
        "namespace {" + os.linesep + \
        "  // comment" + os.linesep + \
        "}// comment" + os.linesep))
    outputs.append((
        "namespace {" + os.linesep + \
        "  // comment" + os.linesep + \
        "}  // namespace" + os.linesep, True, True))

    # namespace
    inputs.append(("./Test.h",
        "namespace hal {" + os.linesep + \
        "  // comment" + os.linesep + \
        "}// comment" + os.linesep))
    outputs.append((
        "namespace hal {" + os.linesep + \
        "  // comment" + os.linesep + \
        "}  // namespace hal" + os.linesep, True, True))

    # namespace with leftover input
    inputs.append(("./Test.h",
        "// comment before namespace" + os.linesep + \
        "namespace hal {" + os.linesep + \
        "  // comment" + os.linesep + \
        "}// comment" + os.linesep + \
        "// comment after namespace" + os.linesep))
    outputs.append((
        "// comment before namespace" + os.linesep + \
        "namespace hal {" + os.linesep + \
        "  // comment" + os.linesep + \
        "}  // namespace hal" + os.linesep + \
        "// comment after namespace" + os.linesep, True, True))

    # Braces within namespace
    inputs.append(("./Test.h",
        "namespace {" + os.linesep + \
        os.linesep + \
        "struct AnalogGyro {" + os.linesep + \
        "  HAL_AnalogInputHandle handle;" + os.linesep + \
        "  double voltsPerDegreePerSecond;" + os.linesep + \
        "  double offset;" + os.linesep + \
        "  int32_t center;" + os.linesep + \
        "}" + os.linesep + \
        os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "namespace {" + os.linesep + \
        os.linesep + \
        "struct AnalogGyro {" + os.linesep + \
        "  HAL_AnalogInputHandle handle;" + os.linesep + \
        "  double voltsPerDegreePerSecond;" + os.linesep + \
        "  double offset;" + os.linesep + \
        "  int32_t center;" + os.linesep + \
        "}" + os.linesep + \
        os.linesep + \
        "}  // namespace" + os.linesep, True, True))

    # extern "C"
    inputs.append(("./Test.h",
        "extern \"C\" {" + os.linesep + \
        "    // nothing" + os.linesep + \
        "}// comment" + os.linesep))
    outputs.append((
        "extern \"C\" {" + os.linesep + \
        "    // nothing" + os.linesep + \
        "}  // extern \"C\"" + os.linesep, True, True))

    # Nested brackets should be handled properly
    inputs.append(("./Test.cpp",
        "extern \"C\" {" + os.linesep + \
        "void func() {" + os.linesep + \
        "  if (1) {" + os.linesep + \
        "  } else if (1) {" + os.linesep + \
        "  } else {" + os.linesep + \
        "  }" + os.linesep + \
        "}" + os.linesep + \
        "}  // extern \"C\"" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    # Handle single-line statements correctly
    inputs.append(("./Test.cpp",
                   "namespace hal { Type typeName; }" + os.linesep))
    outputs.append(
        ("namespace hal { Type typeName; }  // namespace hal" + os.linesep,
         True, True))

    # Two incorrect comments
    inputs.append(("./Test.h",
        "namespace {" + os.linesep + \
        "    // nothing" + os.linesep + \
        "}// comment" + os.linesep + \
        "namespace Name {" + os.linesep + \
        "    // nothing" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "namespace {" + os.linesep + \
        "    // nothing" + os.linesep + \
        "}  // namespace" + os.linesep + \
        "namespace Name {" + os.linesep + \
        "    // nothing" + os.linesep + \
        "}  // namespace Name" + os.linesep, True, True))

    # Don't touch correct comment
    inputs.append(("./Test.h",
        "namespace {" + os.linesep + \
        "    // nothing" + os.linesep + \
        "}  // namespace" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    assert len(inputs) == len(outputs)

    config_file = Config(os.path.abspath(os.getcwd()), ".styleguide")
    for i in range(len(inputs)):
        output, file_changed, success = task.run_pipeline(
            config_file, inputs[i][0], inputs[i][1])
        assert output == outputs[i][0]
        assert file_changed == outputs[i][1]
        assert success == outputs[i][2]
