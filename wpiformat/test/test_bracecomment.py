from wpiformat.bracecomment import BraceComment

from .test_tasktest import *


def test_bracecomment():
    test = TaskTest(BraceComment())

    # Empty anonymous namespace
    test.add_input(
        "./Test.h",
        """namespace {
}// comment
""",
    )
    test.add_output(
        """namespace {
}  // namespace
""",
        True,
    )

    # Anonymous namespace containing comment
    test.add_input(
        "./Test.h",
        """namespace {
  // comment
}// comment
""",
    )
    test.add_output(
        """namespace {
  // comment
}  // namespace
""",
        True,
    )

    # namespace
    test.add_input(
        "./Test.h",
        """namespace hal {
  // comment
}// comment
""",
    )
    test.add_output(
        """namespace hal {
  // comment
}  // namespace hal
""",
        True,
    )

    # namespace with leftover input
    test.add_input(
        "./Test.h",
        """// comment before namespace
namespace hal {
  // comment
}// comment
// comment after namespace
""",
    )
    test.add_output(
        """// comment before namespace
namespace hal {
  // comment
}  // namespace hal
// comment after namespace
""",
        True,
    )

    # Braces within namespace
    test.add_input(
        "./Test.h",
        """namespace {

struct AnalogGyro {
  HAL_AnalogInputHandle handle;
  double voltsPerDegreePerSecond;
  double offset;
  int32_t center;
}

}
""",
    )
    test.add_output(
        """namespace {

struct AnalogGyro {
  HAL_AnalogInputHandle handle;
  double voltsPerDegreePerSecond;
  double offset;
  int32_t center;
}

}  // namespace
""",
        True,
    )

    # extern "C"
    test.add_input(
        "./Test.h",
        """extern "C" {
    // nothing
}// comment
""",
    )
    test.add_output(
        """extern "C" {
    // nothing
}  // extern "C"
""",
        True,
    )

    # Nested brackets should be handled properly
    test.add_input(
        "./Test.cpp",
        """extern "C" {
void func() {
  if (1) {
  } else if (1) {
  } else {
  }
}
}  // extern "C"
""",
    )
    test.add_latest_input_as_output(True)

    # Nested brackets on same line
    test.add_input(
        "./Test.cpp",
        """namespace wpi {
{{}}
}  // namespace java
""",
    )
    test.add_output(
        """namespace wpi {
{{}}
}  // namespace wpi
""",
        True,
    )

    # Handle single-line statements correctly
    test.add_input("./Test.cpp", "namespace hal { Type typeName; }\n")
    test.add_output("namespace hal { Type typeName; }  // namespace hal\n", True)

    # Two incorrect comments
    test.add_input(
        "./Test.h",
        """namespace {
    // nothing
}// comment
namespace Name {
    // nothing
}
""",
    )
    test.add_output(
        """namespace {
    // nothing
}  // namespace
namespace Name {
    // nothing
}  // namespace Name
""",
        True,
    )

    # Don't touch correct comment
    test.add_input(
        "./Test.h",
        """namespace {
    // nothing
}  // namespace
""",
    )
    test.add_latest_input_as_output(True)

    # Handle braces in comments properly
    test.add_input(
        "./Path.h",
        """#ifndef ALLWPILIB_WPI_PATH_H_
#define ALLWPILIB_WPI_PATH_H_

namespace wpi {
namespace sys {
namespace path {

/// @{

}  // end namespace path
}  // namespace sys
}  // namespace wpi

#endif  // ALLWPILIB_WPI_PATH_H_
""",
    )
    test.add_output(
        """#ifndef ALLWPILIB_WPI_PATH_H_
#define ALLWPILIB_WPI_PATH_H_

namespace wpi {
namespace sys {
namespace path {

/// @{

}  // namespace path
}  // namespace sys
}  // namespace wpi

#endif  // ALLWPILIB_WPI_PATH_H_
""",
        True,
    )

    test.run(OutputType.FILE)
