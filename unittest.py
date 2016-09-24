#!/usr/bin/env python3

from datetime import date
import os

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
