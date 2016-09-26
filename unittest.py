#!/usr/bin/env python3

from datetime import date
import os

from includeorder import IncludeOrder
from licenseupdate import LicenseUpdate
from newline import Newline
from stdlib import Stdlib
from whitespace import Whitespace

def test(task, inputs, outputs):
    if len(inputs) != len(outputs):
        print("Error: number of test inputs != number of test outputs")
        return 1

    print(type(task).__name__)

    success = True
    print_str = "  test {}/{}: {}"
    for i in range(0, len(inputs)):
        print("  ".format(type(task).__name__), end = "")
        output, file_changed = task.run(inputs[i][0], inputs[i][1])
        if output != outputs[i][0] or file_changed != outputs[i][1]:
            success = False

            print(print_str.format(i + 1, len(inputs), "FAIL"))

            print("expected file_changed == {} and output ==".format(
                outputs[i][1]))
            print(outputs[i][0].encode())

            print(os.linesep + "actual file_changed == {} and output ==".format(
                file_changed))
            print(output.encode())
        else:
            print(print_str.format(i + 1, len(inputs), "OK"))
    return success

def test_includeorder():
    task = IncludeOrder()

    inputs = []
    outputs = []

    # cpp source including related header with wrong include braces and C++ sys
    # before C sys headers
    inputs.append(("./Utility.cpp",
        "#include <Utility.h>" + os.linesep + \
        os.linesep + \
        "#include <sstream>" + os.linesep + \
        os.linesep + \
        "#include <cxxabi.h>" + os.linesep + \
        "#include <execinfo.h>" + os.linesep + \
        os.linesep + \
        "#include \"HAL/HAL.h\"" + os.linesep + \
        "#include \"Task.h\"" + os.linesep + \
        "#include \"nivision.h\"" + os.linesep))
    outputs.append((
        "#include \"Utility.h\"" + os.linesep + \
        os.linesep + \
        "#include <cxxabi.h>" + os.linesep + \
        "#include <execinfo.h>" + os.linesep + \
        os.linesep + \
        "#include <sstream>" + os.linesep + \
        os.linesep + \
        "#include \"HAL/HAL.h\"" + os.linesep + \
        "#include \"Task.h\"" + os.linesep + \
        "#include \"nivision.h\"" + os.linesep, True))

    # Ensure quotes around C and C++ std header includes are replaced with
    # angle brackets and they are properly sorted into two groups
    inputs.append(("./Test.h",
        "#include \"stdio.h\"" + os.linesep + \
        "#include \"iostream\"" + os.linesep + \
        "#include \"memory\"" + os.linesep + \
        "#include \"signal.h\"" + os.linesep))
    outputs.append((
        "#include <signal.h>" + os.linesep + \
        "#include <stdio.h>" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep + \
        "#include <memory>" + os.linesep, True))

    # Ensure NOLINT headers are considered related headers
    inputs.append(("./Test.h",
        "#include <cstdio>" + os.linesep + \
        "#include \"ImportantHeader.h\"  // NOLINT" + os.linesep))
    outputs.append((
        "#include \"ImportantHeader.h\"  // NOLINT" + os.linesep + \
        os.linesep + \
        "#include <cstdio>" + os.linesep, True))

    # Check sorting for at least one header from each group except related
    # headeer. Test.inc isn't considered related in headers.
    inputs.append(("./Test.h",
        "#include \"MyHeader.h\"" + os.linesep + \
        "#include <stdio.h>" + os.linesep + \
        "#include \"Test.inc\"" + os.linesep + \
        "#include <sys/time.h>" + os.linesep + \
        "#include <fstream>" + os.linesep + \
        "#include <boost/algorithm/string/replace.hpp>" + os.linesep))
    outputs.append((
        "#include <stdio.h>" + os.linesep + \
        "#include <sys/time.h>" + os.linesep + \
        os.linesep + \
        "#include <fstream>" + os.linesep + \
        os.linesep + \
        "#include <boost/algorithm/string/replace.hpp>" + os.linesep + \
        os.linesep + \
        "#include \"MyHeader.h\"" + os.linesep + \
        "#include \"Test.inc\"" + os.linesep, True))

    # Check newline is added between last header and code after it
    inputs.append(("./Test.cpp",
        "#include \"MyFile.h\"" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep + \
        "namespace std {" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "#include <iostream>" + os.linesep + \
        os.linesep + \
        "#include \"MyFile.h\"" + os.linesep + \
        os.linesep + \
        "namespace std {" + os.linesep + \
        "}" + os.linesep, True))

    # Check newlines are removed between last header and code after it
    inputs.append(("./Test.cpp",
        "#include \"MyFile.h\"" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep + \
        os.linesep + \
        os.linesep + \
        os.linesep + \
        "namespace std {" + os.linesep + \
        "}" + os.linesep))
    outputs.append((outputs[len(outputs) - 1][0], True))

    # Ensure headers stay grouped together between license header and other code
    inputs.append(("./Test.cpp",
        "// Copyright (c) Company Name 2016." + os.linesep + \
        "#include <iostream>" + os.linesep + \
        "#include \"Test.h\"" + os.linesep + \
        "namespace std {" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "// Copyright (c) Company Name 2016." + os.linesep + \
        "#include \"Test.h\"" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep + \
        os.linesep + \
        "namespace std {" + os.linesep + \
        "}" + os.linesep, True))

    # Check "#ifdef _WIN32" is sorted after all other includes
    inputs.append(("./Error.h",
        "#pragma once" + os.linesep + \
        os.linesep + \
        "#include <stdint.h>" + os.linesep + \
        os.linesep + \
        "#include <string>" + os.linesep + \
        os.linesep + \
        "#ifdef _WIN32" + os.linesep + \
        "#include <Windows.h>" + os.linesep + \
        "// This is a comment" + os.linesep + \
        "#undef GetMessage" + os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "#include \"Base.h\"" + os.linesep + \
        "#include \"llvm/StringRef.h\"" + os.linesep))
    outputs.append((
        "#pragma once" + os.linesep + \
        os.linesep + \
        "#include <stdint.h>" + os.linesep + \
        os.linesep + \
        "#include <string>" + os.linesep + \
        os.linesep + \
        "#include \"Base.h\"" + os.linesep + \
        "#include \"llvm/StringRef.h\"" + os.linesep + \
        os.linesep + \
        "#ifdef _WIN32" + os.linesep + \
        "#include <Windows.h>" + os.linesep + \
        "// This is a comment" + os.linesep + \
        "#undef GetMessage" + os.linesep + \
        "#endif" + os.linesep, True))

    # Verify relevant headers are found and sorted correctly
    inputs.append(("./PDP.cpp",
        "#include \"HAL/PDP.h\"" + os.linesep + \
        os.linesep + \
        "#include <memory>" + os.linesep + \
        os.linesep + \
        "#include \"ctre/PDP.h\"" + os.linesep + \
        os.linesep + \
        "using namespace hal;" + os.linesep))
    outputs.append((
        "#include \"HAL/PDP.h\"" + os.linesep + \
        os.linesep + \
        "#include <memory>" + os.linesep + \
        os.linesep + \
        "#include \"ctre/PDP.h\"" + os.linesep + \
        os.linesep + \
        "using namespace hal;" + os.linesep, True))

    # Check for idempotence
    inputs.append(("./PDP.cpp", outputs[len(outputs) - 1][0]))
    outputs.append((inputs[len(inputs) - 1][1], False))

    return test(task, inputs, outputs)

def test_licenseupdate():
    task = LicenseUpdate()

    year = str(date.today().year)

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

    # pragma once at top of file
    inputs.append(("./Test.h", file_appendix))
    outputs.append((
    "/*                                Company Name                                */" + os.linesep +
    "/* Copyright (c) Company Name {}. All Rights Reserved.                      */".format(year) +
    os.linesep +
    os.linesep +
    file_appendix, True))

    # pragma once at top of file preceded by newline
    temp = (inputs[len(inputs) - 1][0], os.linesep + inputs[len(inputs) - 1][1])
    inputs.append(temp)
    outputs.append(outputs[len(outputs) - 1])

    # File containing up-to-date license preceded by newline
    inputs.append(("./Test.h",
    os.linesep +
    "/*                                Company Name                                */" + os.linesep +
    "/* Copyright (c) Company Name {}. All Rights Reserved.                      */".format(year) +
    os.linesep +
    os.linesep +
    file_appendix))
    outputs.append((inputs[len(inputs) - 1][1].lstrip(), True))

    # File containing up-to-date range license
    inputs.append(("./Test.h",
    "/*                                Company Name                                */" + os.linesep +
    "// Copyright (c) Company Name 2011-{}. All Rights Reserved.".format(year) +
    os.linesep +
    os.linesep +
    file_appendix))
    outputs.append((
    "/*                                Company Name                                */" + os.linesep +
    "/* Copyright (c) Company Name 2011-{}. All Rights Reserved.                 */".format(year) +
    os.linesep +
    os.linesep +
    file_appendix, True))

    # File containing up-to-date license with one year
    inputs.append(("./Test.h",
    "/*                                Company Name                                */" + os.linesep +
    "/* Copyright (c) Company Name {}. All Rights Reserved.                      */".format(year) +
    os.linesep +
    os.linesep +
    file_appendix))
    outputs.append((inputs[len(inputs) - 1][1], False))

    return test(task, inputs, outputs)

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
    outputs.append((os.linesep, True))

    # No newline
    inputs.append(("./Test.h", file_appendix))
    outputs.append((file_appendix + os.linesep, True))

    # One newline
    inputs.append((inputs[1][0], inputs[1][1] + os.linesep))
    outputs.append((outputs[1][0], False))

    # Two newlines
    inputs.append((inputs[1][0], inputs[1][1] + os.linesep + os.linesep))
    outputs.append((outputs[1][0], True))

    # .bat file with no "./" prefix
    inputs.append(("test.bat", inputs[1][1].replace(os.linesep, "\r\n")))
    outputs.append((outputs[1][0].replace(os.linesep, "\r\n"), True))

    return test(task, inputs, outputs)

def test_stdlib():
    task = Stdlib()

    inputs = []
    outputs = []

    inputs.append(("./Main.cpp",
        "#include <cstdint>" + os.linesep +
        "#include <stdlib.h>" + os.linesep +
        os.linesep +
        "int main() {" + os.linesep +
        "  auto mem = static_cast<std::uint8_t*>(malloc(5));" + os.linesep +
        "  std::int32_t i = 4;" + os.linesep +
        "  int32_t a = -2;" + os.linesep +
        "  std::uint_fast16_t j = 5;" + os.linesep +
        "  std::uint_fast16_t* k = &j;" + os.linesep +
        "  std::uint_fast16_t** l = &k;" + os.linesep +
        "  std::uint_fast16_t ** m = l;" + os.linesep +
        "  free(mem);" + os.linesep +
        "}" + os.linesep))
    outputs.append((
        "#include <stdint.h>" + os.linesep +
        "#include <cstdlib>" + os.linesep +
        os.linesep +
        "int main() {" + os.linesep +
        "  auto mem = static_cast<uint8_t*>(std::malloc(5));" + os.linesep +
        "  int32_t i = 4;" + os.linesep +
        "  int32_t a = -2;" + os.linesep +
        "  uint_fast16_t j = 5;" + os.linesep +
        "  uint_fast16_t* k = &j;" + os.linesep +
        "  uint_fast16_t** l = &k;" + os.linesep +
        "  uint_fast16_t ** m = l;" + os.linesep +
        "  std::free(mem);" + os.linesep +
        "}" + os.linesep, True))

    # FILE should be recognized as type here
    inputs.append(("./Class.cpp", "static FILE* Class::file = nullptr;"))
    outputs.append(("static std::FILE* Class::file = nullptr;", True))

    # FILE should not be recognized as type here
    inputs.append(("./Class.cpp",
        "static int Class::error1 = ERR_FILE;" + os.linesep +
        "#define FILE_LOG(level)" + os.linesep +
        "if (level > FILELog::ReportingLevel())" + os.linesep))
    outputs.append((
        "static int Class::error1 = ERR_FILE;" + os.linesep +
        "#define FILE_LOG(level)" + os.linesep +
        "if (level > FILELog::ReportingLevel())" + os.linesep, False))

    # Types followed by semicolon should match
    inputs.append(("./Main.cpp", "typedef integer std::uint8_t;"))
    outputs.append(("typedef integer uint8_t;", True))

    return test(task, inputs, outputs)

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
    outputs.append(("", False))

    # No trailing whitespace
    inputs.append(("./Test.h", file_appendix))
    outputs.append((file_appendix, False))

    # Two spaces trailing
    inputs.append(("./Test.h",
        "#pragma once" + os.linesep +
        os.linesep +
        "#include <iostream>" + os.linesep +
        os.linesep +
        "int main() {  " + os.linesep +
        "  std::cout << \"Hello World!\";  " + os.linesep +
        "}" + os.linesep))
    outputs.append((file_appendix, True))

    # Two tabs trailing
    inputs.append(("./Test.h",
        "#pragma once" + os.linesep +
        os.linesep +
        "#include <iostream>" + os.linesep +
        os.linesep +
        "int main() {\t\t" + os.linesep +
        "  std::cout << \"Hello World!\";\t\t" + os.linesep +
        "}" + os.linesep))
    outputs.append((file_appendix, True))

    return test(task, inputs, outputs)

def main():
    success = True
    success &= test_includeorder()
    success &= test_licenseupdate()
    success &= test_newline()
    success &= test_stdlib()
    success &= test_whitespace()

    if success:
        return 0
    else:
        return 1

if __name__ == "__main__":
    main()
