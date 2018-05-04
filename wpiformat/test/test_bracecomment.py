import os

from test.tasktest import *
from wpiformat.bracecomment import BraceComment


def test_bracecomment():
    test = TaskTest(BraceComment())

    # Empty anonymous namespace
    test.add_input("./Test.h",
        "namespace {" + os.linesep + \
        "}// comment" + os.linesep)
    test.add_output(
        "namespace {" + os.linesep + \
        "}  // namespace" + os.linesep, True, True)

    # Anonymous namespace containing comment
    test.add_input("./Test.h",
        "namespace {" + os.linesep + \
        "  // comment" + os.linesep + \
        "}// comment" + os.linesep)
    test.add_output(
        "namespace {" + os.linesep + \
        "  // comment" + os.linesep + \
        "}  // namespace" + os.linesep, True, True)

    # namespace
    test.add_input("./Test.h",
        "namespace hal {" + os.linesep + \
        "  // comment" + os.linesep + \
        "}// comment" + os.linesep)
    test.add_output(
        "namespace hal {" + os.linesep + \
        "  // comment" + os.linesep + \
        "}  // namespace hal" + os.linesep, True, True)

    # namespace with leftover input
    test.add_input("./Test.h",
        "// comment before namespace" + os.linesep + \
        "namespace hal {" + os.linesep + \
        "  // comment" + os.linesep + \
        "}// comment" + os.linesep + \
        "// comment after namespace" + os.linesep)
    test.add_output(
        "// comment before namespace" + os.linesep + \
        "namespace hal {" + os.linesep + \
        "  // comment" + os.linesep + \
        "}  // namespace hal" + os.linesep + \
        "// comment after namespace" + os.linesep, True, True)

    # Braces within namespace
    test.add_input("./Test.h",
        "namespace {" + os.linesep + \
        os.linesep + \
        "struct AnalogGyro {" + os.linesep + \
        "  HAL_AnalogInputHandle handle;" + os.linesep + \
        "  double voltsPerDegreePerSecond;" + os.linesep + \
        "  double offset;" + os.linesep + \
        "  int32_t center;" + os.linesep + \
        "}" + os.linesep + \
        os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "namespace {" + os.linesep + \
        os.linesep + \
        "struct AnalogGyro {" + os.linesep + \
        "  HAL_AnalogInputHandle handle;" + os.linesep + \
        "  double voltsPerDegreePerSecond;" + os.linesep + \
        "  double offset;" + os.linesep + \
        "  int32_t center;" + os.linesep + \
        "}" + os.linesep + \
        os.linesep + \
        "}  // namespace" + os.linesep, True, True)

    # extern "C"
    test.add_input("./Test.h",
        "extern \"C\" {" + os.linesep + \
        "    // nothing" + os.linesep + \
        "}// comment" + os.linesep)
    test.add_output(
        "extern \"C\" {" + os.linesep + \
        "    // nothing" + os.linesep + \
        "}  // extern \"C\"" + os.linesep, True, True)

    # Nested brackets should be handled properly
    test.add_input("./Test.cpp",
        "extern \"C\" {" + os.linesep + \
        "void func() {" + os.linesep + \
        "  if (1) {" + os.linesep + \
        "  } else if (1) {" + os.linesep + \
        "  } else {" + os.linesep + \
        "  }" + os.linesep + \
        "}" + os.linesep + \
        "}  // extern \"C\"" + os.linesep)
    test.add_latest_input_as_output(True)

    # Nested brackets on same line
    test.add_input("./Test.cpp",
        "namespace wpi {" + os.linesep + \
        "{{}}" + os.linesep + \
        "}  // namespace java" + os.linesep)
    test.add_output(
        "namespace wpi {" + os.linesep + \
        "{{}}" + os.linesep + \
        "}  // namespace wpi" + os.linesep, True, True)

    # Handle single-line statements correctly
    test.add_input("./Test.cpp",
                   "namespace hal { Type typeName; }" + os.linesep)
    test.add_output(
        "namespace hal { Type typeName; }  // namespace hal" + os.linesep, True,
        True)

    # Two incorrect comments
    test.add_input("./Test.h",
        "namespace {" + os.linesep + \
        "    // nothing" + os.linesep + \
        "}// comment" + os.linesep + \
        "namespace Name {" + os.linesep + \
        "    // nothing" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "namespace {" + os.linesep + \
        "    // nothing" + os.linesep + \
        "}  // namespace" + os.linesep + \
        "namespace Name {" + os.linesep + \
        "    // nothing" + os.linesep + \
        "}  // namespace Name" + os.linesep, True, True)

    # Don't touch correct comment
    test.add_input("./Test.h",
        "namespace {" + os.linesep + \
        "    // nothing" + os.linesep + \
        "}  // namespace" + os.linesep)
    test.add_latest_input_as_output(True)

    # Handle braces in comments properly
    test.add_input("./Path.h",
        "#ifndef ALLWPILIB_WPI_PATH_H_" + os.linesep + \
        "#define ALLWPILIB_WPI_PATH_H_" + os.linesep + \
        os.linesep + \
        "namespace wpi {" + os.linesep + \
        "namespace sys {" + os.linesep + \
        "namespace path {" + os.linesep + \
        os.linesep + \
        "/// @{" + os.linesep + \
        os.linesep + \
        "}  // end namespace path" + os.linesep + \
        "}  // namespace sys" + os.linesep + \
        "}  // namespace wpi" + os.linesep + \
        os.linesep + \
        "#endif  // ALLWPILIB_WPI_PATH_H_" + os.linesep)
    test.add_output(
        "#ifndef ALLWPILIB_WPI_PATH_H_" + os.linesep + \
        "#define ALLWPILIB_WPI_PATH_H_" + os.linesep + \
        os.linesep + \
        "namespace wpi {" + os.linesep + \
        "namespace sys {" + os.linesep + \
        "namespace path {" + os.linesep + \
        os.linesep + \
        "/// @{" + os.linesep + \
        os.linesep + \
        "}  // namespace path" + os.linesep + \
        "}  // namespace sys" + os.linesep + \
        "}  // namespace wpi" + os.linesep + \
        os.linesep + \
        "#endif  // ALLWPILIB_WPI_PATH_H_" + os.linesep, True, True)

    test.run(OutputType.FILE)
