import os

from test.tasktest import *
from wpiformat.stdlib import Stdlib


def test_stdlib():
    test = TaskTest(Stdlib())

    test.add_input("./Main.cpp",
        "#include <cstdint>" + os.linesep + \
        "#include <stdlib.h>" + os.linesep + \
        os.linesep + \
        "int main() {" + os.linesep + \
        "  auto mem = static_cast<std::uint8_t*>(malloc(5));" + os.linesep + \
        "  std::int32_t i = 4;" + os.linesep + \
        "  int32_t a = -2;" + os.linesep + \
        "  std::uint_fast16_t j = 5;" + os.linesep + \
        "  std::uint_fast16_t* k = &j;" + os.linesep + \
        "  std::uint_fast16_t** l = &k;" + os.linesep + \
        "  std::uint_fast16_t ** m = l;" + os.linesep + \
        "  free(mem);" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "#include <stdint.h>" + os.linesep + \
        "#include <cstdlib>" + os.linesep + \
        os.linesep + \
        "int main() {" + os.linesep + \
        "  auto mem = static_cast<uint8_t*>(std::malloc(5));" + os.linesep + \
        "  int32_t i = 4;" + os.linesep + \
        "  int32_t a = -2;" + os.linesep + \
        "  uint_fast16_t j = 5;" + os.linesep + \
        "  uint_fast16_t* k = &j;" + os.linesep + \
        "  uint_fast16_t** l = &k;" + os.linesep + \
        "  uint_fast16_t ** m = l;" + os.linesep + \
        "  std::free(mem);" + os.linesep + \
        "}" + os.linesep, True, True)

    # FILE should be recognized as type here
    test.add_input("./Class.cpp", "static FILE* Class::file = nullptr;")
    test.add_output("static std::FILE* Class::file = nullptr;", True, True)

    # FILE should not be recognized as type here
    test.add_input("./Class.cpp",
        "static int Class::error1 = ERR_FILE;" + os.linesep + \
        "#define FILE_LOG(level)" + os.linesep + \
        "if (level > FILELog::ReportingLevel())" + os.linesep)
    test.add_output(
        "static int Class::error1 = ERR_FILE;" + os.linesep + \
        "#define FILE_LOG(level)" + os.linesep + \
        "if (level > FILELog::ReportingLevel())" + os.linesep, False, True)

    # Remove "std::" from beginning of line
    test.add_input("./Class.cpp",
                   "/**" + os.linesep + \
                   " *" + os.linesep + \
                   " */" + os.linesep + \
                   "std::size_t SizeUleb128(uint64_t val) {" + os.linesep + \
                   "  uint32_t result = 0;" + os.linesep)
    test.add_output("/**" + os.linesep + \
                    " *" + os.linesep + \
                    " */" + os.linesep + \
                    "size_t SizeUleb128(uint64_t val) {" + os.linesep + \
                    "  uint32_t result = 0;" + os.linesep, True, True)

    # Remove "std::" from beginning of file
    test.add_input("./Class.cpp",
                   "std::size_t SizeUleb128(uint64_t val) {" + os.linesep + \
                   "  uint32_t result = 0;" + os.linesep)
    test.add_output("size_t SizeUleb128(uint64_t val) {" + os.linesep + \
                    "  uint32_t result = 0;" + os.linesep, True, True)

    # Don't prepend "std::" to function name if it's a function definition
    # "time()" in other contexts is a C standard library function.
    test.add_input(
        "./Test.cpp",
        "uint64_t time() const { return m_val.last_change; }" + os.linesep)
    test.add_latest_input_as_output(True)

    # Test detection of type within static_cast<>
    test.add_input("./Test.cpp", "static_cast<std::uint64_t>(x);" + os.linesep)
    test.add_output("static_cast<uint64_t>(x);" + os.linesep, True, True)

    # Test detection of type with "-" prefix
    test.add_input("./Test.cpp", "-atan(140 / 76.44);" + os.linesep)
    test.add_output("-std::atan(140 / 76.44);" + os.linesep, True, True)

    # Types followed by semicolon should match
    test.add_input("./Main.cpp", "typedef integer std::uint8_t;")
    test.add_output("typedef integer uint8_t;", True, True)

    test.run(OutputType.FILE)
