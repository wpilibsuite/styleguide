#!/usr/bin/env python3

from datetime import date
import io
import os
import sys

from includeorder import IncludeOrder
from licenseupdate import LicenseUpdate
from namespace import Namespace
from newline import Newline
from stdlib import Stdlib
from whitespace import Whitespace


def test(task, inputs, outputs, stdout_as_output=False):
    if len(inputs) != len(outputs):
        print("Error: number of test inputs != number of test outputs")
        return 1

    print(type(task).__name__)

    if stdout_as_output:
        saved_stdout = sys.stdout

    tests_passed = True
    print_str = "  test {}/{}: {}"
    for i in range(len(inputs)):
        print("  ".format(type(task).__name__), end="")

        if stdout_as_output:
            new_stdout = io.StringIO()
            sys.stdout = new_stdout
            unused_output, file_changed, success = \
                task.run(inputs[i][0], inputs[i][1])
            sys.stdout = saved_stdout
            new_stdout.seek(0)
            output = new_stdout.read()
        else:
            output, file_changed, success = task.run(inputs[i][0], inputs[i][1])

        if output != outputs[i][0] or file_changed != outputs[i][1] or \
                success != outputs[i][2]:
            tests_passed = False

            print(print_str.format(i + 1, len(inputs), "FAIL"))

            output_str = "expected file_changed == {}, success == {}, and " + \
                         "output =="
            print(output_str.format(outputs[i][1], outputs[i][2]))
            print(outputs[i][0].encode())

            output_str = "actual file_changed == {}, success == {}, and " + \
                         "output =="
            print(os.linesep + output_str.format(file_changed, success))
            print(output.encode())
        else:
            print(print_str.format(i + 1, len(inputs), "OK"))
    return tests_passed


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
        "#include \"nivision.h\"" + os.linesep, True, True))

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
        "#include <memory>" + os.linesep, True, True))

    # Ensure NOLINT headers are considered related headers
    inputs.append(("./Test.h",
        "#include <cstdio>" + os.linesep + \
        "#include \"ImportantHeader.h\"  // NOLINT" + os.linesep))
    outputs.append((
        "#include \"ImportantHeader.h\"  // NOLINT" + os.linesep + \
        os.linesep + \
        "#include <cstdio>" + os.linesep, True, True))

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
        "#include \"Test.inc\"" + os.linesep, True, True))

    # Check "other header" isn't identified as C system include
    inputs.append(("./Test.h",
        "#include <OtherHeader.h>" + os.linesep + \
        "#include <sys/time.h>" + os.linesep))
    outputs.append((
        "#include <sys/time.h>" + os.linesep + \
        os.linesep + \
        "#include <OtherHeader.h>" + os.linesep, True, True))

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
        "}" + os.linesep, True, True))

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
    outputs.append((outputs[len(outputs) - 1][0], True, True))

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
        "}" + os.linesep, True, True))

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
        "#endif" + os.linesep, True, True))

    # Verify relevant headers are found and sorted correctly
    inputs.append(("./PDP.cpp",
        "#include <memory>" + os.linesep + \
        os.linesep + \
        "#include \"HAL/PDP.h\"" + os.linesep + \
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
        "using namespace hal;" + os.linesep, True, True))

    # Check for idempotence
    inputs.append(("./PDP.cpp", outputs[len(outputs) - 1][0]))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

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
        "/*                                Company Name                                */"
        + os.linesep +
        "/* Copyright (c) Company Name {}. All Rights Reserved.                      */".
        format(year) + os.linesep + os.linesep + file_appendix, True, True))

    # pragma once at top of file preceded by newline
    temp = (inputs[len(inputs) - 1][0], os.linesep + inputs[len(inputs) - 1][1])
    inputs.append(temp)
    outputs.append(outputs[len(outputs) - 1])

    # File containing up-to-date license preceded by newline
    inputs.append((
        "./Test.h", os.linesep +
        "/*                                Company Name                                */"
        + os.linesep +
        "/* Copyright (c) Company Name {}. All Rights Reserved.                      */".
        format(year) + os.linesep + os.linesep + file_appendix))
    outputs.append((inputs[len(inputs) - 1][1].lstrip(), True, True))

    # File containing up-to-date range license
    inputs.append((
        "./Test.h",
        "/*                                Company Name                                */"
        + os.linesep +
        "// Copyright (c) Company Name 2011-{}. All Rights Reserved.".format(
            year) + os.linesep + os.linesep + file_appendix))
    outputs.append((
        "/*                                Company Name                                */"
        + os.linesep +
        "/* Copyright (c) Company Name 2011-{}. All Rights Reserved.                 */".
        format(year) + os.linesep + os.linesep + file_appendix, True, True))

    # File containing up-to-date license with one year
    inputs.append((
        "./Test.h",
        "/*                                Company Name                                */"
        + os.linesep +
        "/* Copyright (c) Company Name {}. All Rights Reserved.                      */".
        format(year) + os.linesep + os.linesep + file_appendix))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    # File with three newlines between license and include guard
    inputs.append((
        "./Test.h",
        "/*                                Company Name                                */"
        + os.linesep +
        "/* Copyright (c) Company Name {}. All Rights Reserved.                      */".
        format(year) + os.linesep + os.linesep + os.linesep + file_appendix))
    outputs.append((outputs[len(outputs) - 1][0], True, True))

    # File with only one newline between license and include guard
    inputs.append((
        "./Test.h",
        "/*                                Company Name                                */"
        + os.linesep +
        "/* Copyright (c) Company Name {}. All Rights Reserved.                      */".
        format(year) + os.linesep + file_appendix))
    outputs.append((outputs[len(outputs) - 1][0], True, True))

    # File with multiline comment spanning multiple lines of license header
    inputs.append((
        "./Test.h", "/*" + os.linesep +
        " * Autogenerated file! Do not manually edit this file. This version is regenerated"
        + os.linesep +
        " * any time the publish task is run, or when this file is deleted." +
        os.linesep + " */" + os.linesep + os.linesep +
        "const char* WPILibVersion = \"\";"))
    outputs.append((
        "/*                                Company Name                                */"
        + os.linesep +
        "/* Copyright (c) Company Name {}. All Rights Reserved.                      */".
        format(year) + os.linesep + os.linesep + inputs[len(inputs) - 1][1],
        True, True))

    return test(task, inputs, outputs)


def test_namespace():
    task = Namespace()

    inputs = []
    outputs = []

    # Before class block
    inputs.append(("./Test.h",
        "using std::chrono;" + os.linesep + \
        "class Test {" + os.linesep + \
        "}" + os.linesep))
    outputs.append(("./Test.h: 1: 'using std::chrono;' in global namespace\n",
                    False, False))

    # Inside enum block
    inputs.append(("./Test.h",
        "enum Test {" + os.linesep + \
        "  using std::chrono;" + os.linesep + \
        "}" + os.linesep))
    outputs.append(("", False, True))

    # After { block
    inputs.append(("./Test.h",
        "{" + os.linesep + \
        "}" + os.linesep + \
        "using std::chrono;" + os.linesep))
    outputs.append(("./Test.h: 3: 'using std::chrono;' in global namespace\n",
                    False, False))

    # Before class block with NOLINT
    inputs.append(("./Test.h",
        "using std::chrono;  // NOLINT" + os.linesep + \
        "class Test {" + os.linesep + \
        "}" + os.linesep))
    outputs.append(("", False, True))

    return test(task, inputs, outputs, True)


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

    return test(task, inputs, outputs)


def test_stdlib():
    task = Stdlib()

    inputs = []
    outputs = []

    inputs.append(
        ("./Main.cpp", "#include <cstdint>" + os.linesep + "#include <stdlib.h>"
         + os.linesep + os.linesep + "int main() {" + os.linesep +
         "  auto mem = static_cast<std::uint8_t*>(malloc(5));" + os.linesep +
         "  std::int32_t i = 4;" + os.linesep + "  int32_t a = -2;" + os.linesep
         + "  std::uint_fast16_t j = 5;" + os.linesep +
         "  std::uint_fast16_t* k = &j;" + os.linesep +
         "  std::uint_fast16_t** l = &k;" + os.linesep +
         "  std::uint_fast16_t ** m = l;" + os.linesep + "  free(mem);" +
         os.linesep + "}" + os.linesep))
    outputs.append(
        ("#include <stdint.h>" + os.linesep + "#include <cstdlib>" + os.linesep
         + os.linesep + "int main() {" + os.linesep +
         "  auto mem = static_cast<uint8_t*>(std::malloc(5));" + os.linesep +
         "  int32_t i = 4;" + os.linesep + "  int32_t a = -2;" + os.linesep +
         "  uint_fast16_t j = 5;" + os.linesep + "  uint_fast16_t* k = &j;" +
         os.linesep + "  uint_fast16_t** l = &k;" + os.linesep +
         "  uint_fast16_t ** m = l;" + os.linesep + "  std::free(mem);" +
         os.linesep + "}" + os.linesep, True, True))

    # FILE should be recognized as type here
    inputs.append(("./Class.cpp", "static FILE* Class::file = nullptr;"))
    outputs.append(("static std::FILE* Class::file = nullptr;", True, True))

    # FILE should not be recognized as type here
    inputs.append(("./Class.cpp", "static int Class::error1 = ERR_FILE;" +
                   os.linesep + "#define FILE_LOG(level)" + os.linesep +
                   "if (level > FILELog::ReportingLevel())" + os.linesep))
    outputs.append(
        ("static int Class::error1 = ERR_FILE;" + os.linesep +
         "#define FILE_LOG(level)" + os.linesep +
         "if (level > FILELog::ReportingLevel())" + os.linesep, False, True))

    # Types followed by semicolon should match
    inputs.append(("./Main.cpp", "typedef integer std::uint8_t;"))
    outputs.append(("typedef integer uint8_t;", True, True))

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

    return test(task, inputs, outputs)


def main():
    success = True
    success &= test_includeorder()
    success &= test_licenseupdate()
    success &= test_namespace()
    success &= test_newline()
    success &= test_stdlib()
    success &= test_whitespace()

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
