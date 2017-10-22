import os

from wpiformat.config import Config
from wpiformat.stdlib import Stdlib


def test_stdlib():
    task = Stdlib()

    inputs = []
    outputs = []

    inputs.append(("./Main.cpp",
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
        "}" + os.linesep))
    outputs.append((
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
        "}" + os.linesep, True, True))

    # FILE should be recognized as type here
    inputs.append(("./Class.cpp", "static FILE* Class::file = nullptr;"))
    outputs.append(("static std::FILE* Class::file = nullptr;", True, True))

    # FILE should not be recognized as type here
    inputs.append(("./Class.cpp",
        "static int Class::error1 = ERR_FILE;" + os.linesep + \
        "#define FILE_LOG(level)" + os.linesep + \
        "if (level > FILELog::ReportingLevel())" + os.linesep))
    outputs.append((
        "static int Class::error1 = ERR_FILE;" + os.linesep + \
        "#define FILE_LOG(level)" + os.linesep + \
        "if (level > FILELog::ReportingLevel())" + os.linesep, False, True))

    # Don't prepend "std::" to function name if it's a function definition
    inputs.append(
        ("./Test.cpp",
         "uint64_t time() const { return m_val.last_change; }" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    # Test detection of type within static_cast<>
    inputs.append(("./Test.cpp", "static_cast<std::uint64_t>(x);" + os.linesep))
    outputs.append(("static_cast<uint64_t>(x);" + os.linesep, True, True))

    # Types followed by semicolon should match
    inputs.append(("./Main.cpp", "typedef integer std::uint8_t;"))
    outputs.append(("typedef integer uint8_t;", True, True))

    assert len(inputs) == len(outputs)

    config_file = Config(os.path.abspath(os.getcwd()), ".styleguide")
    for i in range(len(inputs)):
        output, file_changed, success = task.run_pipeline(
            config_file, inputs[i][0], inputs[i][1])
        assert output == outputs[i][0]
        assert file_changed == outputs[i][1]
        assert success == outputs[i][2]
