import os

from wpiformat.includeorder import IncludeOrder


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

    # Verify subgroups are sorted
    inputs.append(("./PDP.cpp",
        "#include \"support/jni_util.h\"" + os.linesep + \
        "#include \"llvm/SmallString.h\"" + os.linesep + \
        "#include \"llvm/raw_ostream.h\"" + os.linesep))
    outputs.append((
        "#include \"llvm/SmallString.h\"" + os.linesep + \
        "#include \"llvm/raw_ostream.h\"" + os.linesep + \
        "#include \"support/jni_util.h\"" + os.linesep, True, True))

    # Check duplicate headers are removed
    inputs.append(("./PDP.cpp",
        "#include <memory>" + os.linesep + \
        "#include \"ctre/PDP.h\"" + os.linesep + \
        os.linesep + \
        "#include \"HAL/PDP.h\"" + os.linesep + \
        os.linesep + \
        "#include \"ctre/PDP.h\"" + os.linesep + \
        "#include <memory>" + os.linesep + \
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

    # Check source file inclusion is disallowed
    inputs.append(("./Test.h",
        "#include <memory>" + os.linesep + \
        os.linesep + \
        "#include \"Stuff.cpp\"" + os.linesep, False, False))
    outputs.append((inputs[len(inputs) - 1][1], False, False))

    assert len(inputs) == len(outputs)

    for i in range(len(inputs)):
        output, file_changed, success = task.run(inputs[i][0], inputs[i][1])
        assert output == outputs[i][0]
        assert file_changed == outputs[i][1]
        assert success == outputs[i][2]
