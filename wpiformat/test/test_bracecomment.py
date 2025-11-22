import subprocess
from pathlib import Path

from wpiformat.bracecomment import BraceComment

from .test_tasktest import *


def test_bracecomment():
    with OpenTemporaryDirectory():
        subprocess.run(["git", "init", "-q"])
        Path(".wpiformat").write_text(
            r"""cppHeaderFileInclude {
  \.h$
}

cppSrcFileInclude {
  \.cpp$
}
"""
        )

        test_h = Path("./Test.h").resolve()
        test_cpp = Path("./Test.cpp").resolve()
        path_h = Path("./Path.h").resolve()

        # Empty anonymous namespace
        run_and_check_file(
            BraceComment(),
            test_h,
            """namespace {
}// comment
""",
            """namespace {
}  // namespace
""",
            True,
        )

        # Anonymous namespace containing comment
        run_and_check_file(
            BraceComment(),
            test_h,
            """namespace {
  // comment
}// comment
""",
            """namespace {
  // comment
}  // namespace
""",
            True,
        )

        # namespace
        run_and_check_file(
            BraceComment(),
            test_h,
            """namespace hal {
  // comment
}// comment
""",
            """namespace hal {
  // comment
}  // namespace hal
""",
            True,
        )

        # namespace with leftover input
        run_and_check_file(
            BraceComment(),
            test_h,
            """// comment before namespace
namespace hal {
  // comment
}// comment
// comment after namespace
""",
            """// comment before namespace
namespace hal {
  // comment
}  // namespace hal
// comment after namespace
""",
            True,
        )

        # Braces within namespace
        run_and_check_file(
            BraceComment(),
            test_h,
            """namespace {

struct AnalogGyro {
  HAL_AnalogInputHandle handle;
  double voltsPerDegreePerSecond;
  double offset;
  int32_t center;
}

}
""",
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
        run_and_check_file(
            BraceComment(),
            test_h,
            """extern "C" {
    // nothing
}// comment
""",
            """extern "C" {
    // nothing
}  // extern "C"
""",
            True,
        )

        # Nested brackets should be handled properly
        contents = """extern "C" {
void func() {
  if (1) {
  } else if (1) {
  } else {
  }
}
}  // extern "C"
"""
        run_and_check_file(BraceComment(), test_cpp, contents, contents, True)

        # Nested brackets on same line
        run_and_check_file(
            BraceComment(),
            test_cpp,
            """namespace wpi {
{{}}
}  // namespace java
""",
            """namespace wpi {
{{}}
}  // namespace wpi
""",
            True,
        )

        # Handle single-line statements correctly
        run_and_check_file(
            BraceComment(),
            test_cpp,
            "namespace hal { Type typeName; }\n",
            "namespace hal { Type typeName; }  // namespace hal\n",
            True,
        )

        # Two incorrect comments
        run_and_check_file(
            BraceComment(),
            test_h,
            """namespace {
    // nothing
}// comment
namespace Name {
    // nothing
}
""",
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
        contents = """namespace {
    // nothing
}  // namespace
"""
        run_and_check_file(BraceComment(), test_h, contents, contents, True)

        # Handle braces in comments properly
        run_and_check_file(
            BraceComment(),
            path_h,
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

        # Comment in macro
        run_and_check_file(
            BraceComment(),
            test_cpp,
            """#define TEST(namespaceName, name, ...) \\
  namespace namespaceName { \\
  using name = __VA_ARGS__; \\
  } \\
  using name = namespaceName::name;
""",
            """#define TEST(namespaceName, name, ...) \\
  namespace namespaceName { \\
  using name = __VA_ARGS__; \\
  }  /* namespace namespaceName */ \\
  using name = namespaceName::name;
""",
            True,
        )
        run_and_check_file(
            BraceComment(),
            test_cpp,
            """#define TEST(namespaceName, name, ...) \\
  namespace namespaceName { \\
  using name = __VA_ARGS__; \\
  } /* namespaceName */\\
  using name = namespaceName::name;
""",
            """#define TEST(namespaceName, name, ...) \\
  namespace namespaceName { \\
  using name = __VA_ARGS__; \\
  }  /* namespace namespaceName */ \\
  using name = namespaceName::name;
""",
            True,
        )
