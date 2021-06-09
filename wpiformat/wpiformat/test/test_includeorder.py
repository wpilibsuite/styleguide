import os

from .tasktest import *
from .tempdir import *
from wpiformat.includeorder import IncludeOrder


def test_includeorder():
    test = TaskTest(IncludeOrder())

    # cpp source including related header with wrong include braces and C++ sys
    # before C sys headers
    test.add_input("./Utility.cpp",
        "#include <Utility.h>" + os.linesep + \
        os.linesep + \
        "#include <sstream>" + os.linesep + \
        os.linesep + \
        "#include <cxxabi.h>" + os.linesep + \
        "#include <execinfo.h>" + os.linesep + \
        os.linesep + \
        "#include \"HAL/HAL.h\"" + os.linesep + \
        "#include \"Task.h\"" + os.linesep + \
        "#include \"nivision.h\"" + os.linesep)
    test.add_output(
        "#include \"Utility.h\"" + os.linesep + \
        os.linesep + \
        "#include <cxxabi.h>" + os.linesep + \
        "#include <execinfo.h>" + os.linesep + \
        os.linesep + \
        "#include <sstream>" + os.linesep + \
        os.linesep + \
        "#include \"HAL/HAL.h\"" + os.linesep + \
        "#include \"Task.h\"" + os.linesep + \
        "#include \"nivision.h\"" + os.linesep, True, True)

    # Ensure quotes around C and C++ std header includes are replaced with
    # angle brackets and they are properly sorted into two groups
    test.add_input("./Test.h",
        "#include \"stdio.h\"" + os.linesep + \
        "#include \"iostream\"" + os.linesep + \
        "#include \"memory\"" + os.linesep + \
        "#include \"signal.h\"" + os.linesep)
    test.add_output(
        "#include <signal.h>" + os.linesep + \
        "#include <stdio.h>" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep + \
        "#include <memory>" + os.linesep, True, True)

    # Ensure NOLINT headers have newlines around them
    test.add_input("./Test.h",
        "#include \"ctre/PDP.h\"  // NOLINT" + os.linesep + \
        "#include \"gtest/gtest.h\"  // NOLINT" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep)
    test.add_output(
        "#include \"ctre/PDP.h\"  // NOLINT" + os.linesep + \
        os.linesep + \
        "#include \"gtest/gtest.h\"  // NOLINT" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep, True, True)

    # Ensure NOLINT headers don't have extra newlines inserted after them
    test.add_input("./Test.h",
        "#include \"ctre/PDP.h\"  // NOLINT" + os.linesep + \
        os.linesep + \
        "#include \"gtest/gtest.h\"  // NOLINT" + os.linesep + \
        os.linesep + \
        "namespace wpi {" + os.linesep)
    test.add_latest_input_as_output(True)

    # Ensure NOLINT headers take precedence over overrides and have newline
    # inserted
    test.add_input("./Test.h",
        "#include \"ctre/PDP.h\"  // NOLINT" + os.linesep + \
        "#include <atomic>" + os.linesep + \
        "#include <condition_variable>" + os.linesep + \
        "#include <thread>" + os.linesep)
    test.add_output(
        "#include \"ctre/PDP.h\"  // NOLINT" + os.linesep + \
        os.linesep + \
        "#include <atomic>" + os.linesep + \
        "#include <condition_variable>" + os.linesep + \
        "#include <thread>" + os.linesep, True, True)

    # Check sorting for at least one header from each group except related
    # header. Test.inc isn't considered related in headers.
    test.add_input("./Test.h",
        "#include \"MyHeader.h\"" + os.linesep + \
        "#include <stdio.h>" + os.linesep + \
        "#include \"Test.inc\"" + os.linesep + \
        "#include <sys/time.h>" + os.linesep + \
        "#include <fstream>" + os.linesep + \
        "#include <boost/algorithm/string/replace.hpp>" + os.linesep)
    test.add_output(
        "#include <stdio.h>" + os.linesep + \
        "#include <sys/time.h>" + os.linesep + \
        os.linesep + \
        "#include <fstream>" + os.linesep + \
        os.linesep + \
        "#include <boost/algorithm/string/replace.hpp>" + os.linesep + \
        os.linesep + \
        "#include \"MyHeader.h\"" + os.linesep + \
        "#include \"Test.inc\"" + os.linesep, True, True)

    # Verify "other header" isn't identified as C system include
    test.add_input("./Test.h",
        "#include <OtherHeader.h>" + os.linesep + \
        "#include <sys/time.h>" + os.linesep)
    test.add_output(
        "#include <sys/time.h>" + os.linesep + \
        os.linesep + \
        "#include <OtherHeader.h>" + os.linesep, True, True)

    # Verify newline is added between last header and code after it
    test.add_input("./Test.cpp",
        "#include \"MyFile.h\"" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep + \
        "namespace std {" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "#include <iostream>" + os.linesep + \
        os.linesep + \
        "#include \"MyFile.h\"" + os.linesep + \
        os.linesep + \
        "namespace std {" + os.linesep + \
        "}" + os.linesep, True, True)

    # Verify newlines are removed between last header and code after it
    test.add_input("./Test.cpp",
        "#include \"MyFile.h\"" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep + \
        os.linesep + \
        os.linesep + \
        os.linesep + \
        "namespace std {" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "#include <iostream>" + os.linesep + \
        os.linesep + \
        "#include \"MyFile.h\"" + os.linesep + \
        os.linesep + \
        "namespace std {" + os.linesep + \
        "}" + os.linesep, True, True)

    # Ensure extra newlines aren't added between ifdef blocks
    test.add_input("./Test.h",
        "#include <stdint.h>" + os.linesep + \
        os.linesep + \
        "#ifdef __cplusplus" + os.linesep + \
        "#include <cstddef>" + os.linesep + \
        "#else" + os.linesep + \
        "#include <stddef.h>" + os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "#ifdef __cplusplus" + os.linesep + \
        "extern \"C\" {" + os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "struct CvMat;" + os.linesep)
    test.add_latest_input_as_output(True)

    # Ensure headers stay grouped together between license header and other code
    test.add_input("./Test.cpp",
        "// Copyright (c) Company Name 2016." + os.linesep + \
        "#include <iostream>" + os.linesep + \
        "#include \"Test.h\"" + os.linesep + \
        "namespace std {" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "// Copyright (c) Company Name 2016." + os.linesep + \
        "#include \"Test.h\"" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep + \
        os.linesep + \
        "namespace std {" + os.linesep + \
        "}" + os.linesep, True, True)

    # Verify headers are sorted across #ifdef
    test.add_input("./Error.h",
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
        "#include <string>" + os.linesep + \
        os.linesep + \
        "#include \"Base.h\"" + os.linesep + \
        "#include \"llvm/StringRef.h\"" + os.linesep)
    test.add_output(
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
        "#include \"llvm/StringRef.h\"" + os.linesep, True, True)

    # Verify "#ifdef _WIN32" acts as barrier for out-of-order includes
    test.add_input("./Error.h",
        "#pragma once" + os.linesep + \
        os.linesep + \
        "#include <stdint.h>" + os.linesep + \
        os.linesep + \
        "#include <string>" + os.linesep + \
        os.linesep + \
        "#ifdef _WIN32" + os.linesep + \
        "#include <string>" + os.linesep + \
        os.linesep + \
        "#include <Windows.h>" + os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "#include <string>" + os.linesep + \
        os.linesep + \
        "#include \"Base.h\"" + os.linesep + \
        "#include \"llvm/StringRef.h\"" + os.linesep)
    test.add_latest_input_as_output(True)

    # Verify "#ifdef __linux__" is sorted in correct category below other
    # headers
    test.add_input("./Error.h",
        "#pragma once" + os.linesep + \
        os.linesep + \
        "#include <stdlib.h>" + os.linesep + \
        os.linesep + \
        "#include <string>" + os.linesep + \
        os.linesep + \
        "#ifdef __linux__" + os.linesep + \
        "#include <stdio.h>" + os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "#include \"Base.h\"" + os.linesep + \
        "#include \"llvm/StringRef.h\"" + os.linesep)
    test.add_output(
        "#pragma once" + os.linesep + \
        os.linesep + \
        "#include <stdlib.h>" + os.linesep + \
        os.linesep + \
        "#ifdef __linux__" + os.linesep + \
        "#include <stdio.h>" + os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "#include <string>" + os.linesep + \
        os.linesep + \
        "#include \"Base.h\"" + os.linesep + \
        "#include \"llvm/StringRef.h\"" + os.linesep, True, True)

    # Verify "#ifdef __linux__" is included in output if no headers are in same
    # category
    test.add_input("./Error.h",
        "#pragma once" + os.linesep + \
        os.linesep + \
        "#ifdef __linux__" + os.linesep + \
        "#include <stdio.h>" + os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "#include <string>" + os.linesep + \
        os.linesep + \
        "#include \"Base.h\"" + os.linesep + \
        "#include \"llvm/StringRef.h\"" + os.linesep)
    test.add_latest_input_as_output(True)

    # Verify #ifdef blocks in a row are handled properly
    test.add_input("./Log.cpp",
        "#include \"Log.h\"" + os.linesep + \
        os.linesep + \
        "#include <cstdio>" + os.linesep + \
        os.linesep + \
        "#ifdef _WIN32" + os.linesep + \
        "#include <cstdlib>" + os.linesep + \
        "#else" + os.linesep + \
        "#include <cstring>" + os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "#ifdef __APPLE__" + os.linesep + \
        "#include <libgen.h>" + os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "#ifdef __ANDROID__" + os.linesep + \
        "#include <libgen.h>" + os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "using namespace cs;" + os.linesep)
    test.add_output(
        "#include \"Log.h\"" + os.linesep + \
        os.linesep + \
        "#ifdef __APPLE__" + os.linesep + \
        "#include <libgen.h>" + os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "#ifdef __ANDROID__" + os.linesep + \
        "#include <libgen.h>" + os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "#include <cstdio>" + os.linesep + \
        os.linesep + \
        "#ifdef _WIN32" + os.linesep + \
        "#include <cstdlib>" + os.linesep + \
        "#else" + os.linesep + \
        "#include <cstring>" + os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "using namespace cs;" + os.linesep, True, True)

    # Verify comments aren't mangled
    test.add_input("./cscore.h",
        "/* C API */" + os.linesep + \
        "#include \"cscore_c.h\"" + os.linesep + \
        os.linesep + \
        "#ifdef __cplusplus" + os.linesep + \
        "/* C++ API */" + os.linesep + \
        "#include \"cscore_cpp.h\"" + os.linesep + \
        "#include \"cscore_oo.h\"" + os.linesep + \
        "#endif /* __cplusplus */" + os.linesep)
    test.add_latest_input_as_output(True)

    # Check recursive #ifdef
    test.add_input("./Test.h",
        "#include <algorithm>" + os.linesep + \
        os.linesep + \
        "#ifdef __linux__" + os.linesep + \
        "#include <sys/socket.h>" + os.linesep + \
        "#include <sys/syscall.h>" + os.linesep + \
        "#ifdef __GNUC__ > 4" + os.linesep + \
        "#include <algorithm>" + os.linesep + \
        "#endif" + os.linesep + \
        "#endif" + os.linesep)
    test.add_output(
        "#include <algorithm>" + os.linesep + \
        os.linesep + \
        "#ifdef __linux__" + os.linesep + \
        "#include <sys/socket.h>" + os.linesep + \
        "#include <sys/syscall.h>" + os.linesep + \
        os.linesep + \
        "#ifdef __GNUC__ > 4" + os.linesep + \
        "#include <algorithm>" + os.linesep + \
        "#endif" + os.linesep + \
        "#endif" + os.linesep, True, True)

    # Verify extra newline from #endif is removed
    test.add_input("./Test.h",
        "#include \"HAL/HAL.h\"" + os.linesep + \
        "#include \"NotifyListener.h\"" + os.linesep + \
        os.linesep + \
        "#ifdef __cplusplus" + os.linesep + \
        "extern \"C\" {" + os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "void HALSIM_ResetSPIAccelerometerData(int32_t index);" + \
        os.linesep)
    test.add_latest_input_as_output(True)

    # Large test
    test.add_input("./UsbCameraImpl.cpp",
        "#include <algorithm>" + os.linesep + \
        os.linesep + \
        "#include \"Handle.h\"" + os.linesep + \
        "#include \"Log.h\"" + os.linesep + \
        "#include \"Notifier.h\"" + os.linesep + \
        "#include \"UsbUtil.h\"" + os.linesep + \
        "#include \"c_util.h\"" + os.linesep + \
        "#include \"cscore_cpp.h\"" + os.linesep + \
        os.linesep + \
        "#ifdef __linux__" + os.linesep + \
        "#include <dirent.h>" + os.linesep + \
        "#include <fcntl.h>" + os.linesep + \
        "#include <libgen.h>" + os.linesep + \
        "#include <linux/kernel.h>" + os.linesep + \
        "#include <linux/types.h>" + os.linesep + \
        "#include <linux/videodev2.h>" + os.linesep + \
        "#include <sys/eventfd.h>" + os.linesep + \
        "#include <sys/inotify.h>" + os.linesep + \
        "#include <sys/ioctl.h>" + os.linesep + \
        "#include <sys/select.h>" + os.linesep + \
        "#include <sys/stat.h>" + os.linesep + \
        "#include <sys/time.h>" + os.linesep + \
        "#include <sys/types.h>" + os.linesep + \
        "#include <unistd.h>" + os.linesep + \
        os.linesep + \
        "#elif defined(_WIN32)" + os.linesep + \
        os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "using namespace cs;" + os.linesep)
    test.add_output(
        "#ifdef __linux__" + os.linesep + \
        "#include <dirent.h>" + os.linesep + \
        "#include <fcntl.h>" + os.linesep + \
        "#include <libgen.h>" + os.linesep + \
        "#include <linux/kernel.h>" + os.linesep + \
        "#include <linux/types.h>" + os.linesep + \
        "#include <linux/videodev2.h>" + os.linesep + \
        "#include <sys/eventfd.h>" + os.linesep + \
        "#include <sys/inotify.h>" + os.linesep + \
        "#include <sys/ioctl.h>" + os.linesep + \
        "#include <sys/select.h>" + os.linesep + \
        "#include <sys/stat.h>" + os.linesep + \
        "#include <sys/time.h>" + os.linesep + \
        "#include <sys/types.h>" + os.linesep + \
        "#include <unistd.h>" + os.linesep + \
        "#elif defined(_WIN32)" + os.linesep + \
        "#endif" + os.linesep + \
        os.linesep + \
        "#include <algorithm>" + os.linesep + \
        os.linesep + \
        "#include \"Handle.h\"" + os.linesep + \
        "#include \"Log.h\"" + os.linesep + \
        "#include \"Notifier.h\"" + os.linesep + \
        "#include \"UsbUtil.h\"" + os.linesep + \
        "#include \"c_util.h\"" + os.linesep + \
        "#include \"cscore_cpp.h\"" + os.linesep + \
        os.linesep + \
        "using namespace cs;" + os.linesep, True, True)

    # Verify relevant headers are found and sorted correctly
    test.add_input("./PDP.cpp",
        "#include <memory>" + os.linesep + \
        os.linesep + \
        "#include \"HAL/PDP.h\"" + os.linesep + \
        os.linesep + \
        "#include \"ctre/PDP.h\"" + os.linesep + \
        os.linesep + \
        "using namespace hal;" + os.linesep)
    test.add_output(
        "#include \"HAL/PDP.h\"" + os.linesep + \
        os.linesep + \
        "#include <memory>" + os.linesep + \
        os.linesep + \
        "#include \"ctre/PDP.h\"" + os.linesep + \
        os.linesep + \
        "using namespace hal;" + os.linesep, True, True)

    # Check for idempotence
    test.add_input("./PDP.cpp",
        "#include \"HAL/PDP.h\"" + os.linesep + \
        os.linesep + \
        "#include <memory>" + os.linesep + \
        os.linesep + \
        "#include \"ctre/PDP.h\"" + os.linesep + \
        os.linesep + \
        "using namespace hal;" + os.linesep)
    test.add_latest_input_as_output(True)

    # Verify subgroups are sorted
    test.add_input("./PDP.cpp",
        "#include \"support/jni_util.h\"" + os.linesep + \
        "#include \"llvm/SmallString.h\"" + os.linesep + \
        "#include \"llvm/raw_ostream.h\"" + os.linesep)
    test.add_output(
        "#include \"llvm/SmallString.h\"" + os.linesep + \
        "#include \"llvm/raw_ostream.h\"" + os.linesep + \
        "#include \"support/jni_util.h\"" + os.linesep, True, True)

    # Verify duplicate headers are removed
    test.add_input("./PDP.cpp",
        "#include <memory>" + os.linesep + \
        "#include \"ctre/PDP.h\"" + os.linesep + \
        os.linesep + \
        "#include \"HAL/PDP.h\"" + os.linesep + \
        os.linesep + \
        "#include \"ctre/PDP.h\"" + os.linesep + \
        "#include <memory>" + os.linesep + \
        os.linesep + \
        "using namespace hal;" + os.linesep)
    test.add_output(
        "#include \"HAL/PDP.h\"" + os.linesep + \
        os.linesep + \
        "#include <memory>" + os.linesep + \
        os.linesep + \
        "#include \"ctre/PDP.h\"" + os.linesep + \
        os.linesep + \
        "using namespace hal;" + os.linesep, True, True)

    # Verify source file inclusion is disallowed
    test.add_input("./Test.h",
        "#include <memory>" + os.linesep + \
        os.linesep + \
        "#include \"Stuff.cpp\"" + os.linesep)
    test.add_latest_input_as_output(False)

    # Ensure commented-out includes are still sorted
    test.add_input("./Test.h",
        "#include \"stdio.h\"" + os.linesep + \
        "#include \"iostream\"" + os.linesep + \
        "// #include \"memory\"" + os.linesep + \
        "#include \"signal.h\"" + os.linesep)
    test.add_output(
        "#include <signal.h>" + os.linesep + \
        "#include <stdio.h>" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep + \
        "// #include <memory>" + os.linesep, True, True)

    # Ensure commented-out includes with space before them are still sorted
    test.add_input("./Test.h",
        " //#include <signal.h>" + os.linesep + \
        "#include <stdio.h>" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep + \
        "#include <memory>" + os.linesep)
    test.add_output(
        "//#include <signal.h>" + os.linesep + \
        "#include <stdio.h>" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep + \
        "#include <memory>" + os.linesep, True, True)

    # Ensure includes with no space between #include and bracket are sorted
    test.add_input("./Test.h",
        "#include<signal.h>" + os.linesep + \
        "#include<stdio.h>" + os.linesep + \
        os.linesep + \
        "#include<iostream>" + os.linesep + \
        "#include<memory>" + os.linesep)
    test.add_output(
        "#include <signal.h>" + os.linesep + \
        "#include <stdio.h>" + os.linesep + \
        os.linesep + \
        "#include <iostream>" + os.linesep + \
        "#include <memory>" + os.linesep, True, True)

    # Ensure lines containing #include that aren't includes are not processed
    test.add_input("./Test.h", "// #included here" + os.linesep)
    test.add_latest_input_as_output(True)

    # Ensure extra newline isn't inserted between #pragma and #ifdef
    test.add_input("./Test.h",
        "#pragma once" + os.linesep + \
        os.linesep + \
        "#ifdef _MSC_VER" + os.linesep + \
        "#endif" + os.linesep)
    test.add_latest_input_as_output(True)

    with OpenTemporaryDirectory():
        with open(".styleguide", "w") as file:
            file.write(r"""cppHeaderFileInclude {
  \.h$
  \.hpp$
  \.inc$
}

includeProject {
  ^ctre/
}
""")
        test.run(OutputType.FILE)
