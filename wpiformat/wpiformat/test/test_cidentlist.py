import os

from .test_tasktest import *
from wpiformat.cidentlist import CIdentList


def test_cidentlist():
    test = TaskTest(CIdentList())

    # Main.cpp: signature for C++ function
    test.add_input(
        "./Main.cpp",
        "int main() {" + os.linesep + "  return 0;" + os.linesep + "}" + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Main.cpp: signature for C function in extern "C" block
    test.add_input(
        "./Main.cpp",
        'extern "C" {'
        + os.linesep
        + "int main() {"
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output(
        'extern "C" {'
        + os.linesep
        + "int main(void) {"
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep
        + "}"
        + os.linesep,
        True,
    )

    # Main.cpp: signature for C function marked extern "C"
    test.add_input(
        "./Main.cpp",
        'extern "C" int main() {'
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output(
        'extern "C" int main(void) {'
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep,
        True,
    )

    # Main.cpp: extern "C++" function nested in extern "C" block
    test.add_input(
        "./Main.cpp",
        'extern "C" {'
        + os.linesep
        + 'extern "C++" int main() {'
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Main.c: signature for C function
    test.add_input(
        "./Main.c",
        "int main() {" + os.linesep + "  return 0;" + os.linesep + "}" + os.linesep,
    )
    test.add_output(
        "int main(void) {" + os.linesep + "  return 0;" + os.linesep + "}" + os.linesep,
        True,
    )

    # Main.c: signature for C++ function in extern "C++" block
    test.add_input(
        "./Main.c",
        'extern "C++" {'
        + os.linesep
        + "int main() {"
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Main.c: signature for C++ function marked extern "C++"
    test.add_input(
        "./Main.c",
        'extern "C++" int main() {'
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Main.c: extern "C" function nested in extern "C++" block
    test.add_input(
        "./Main.c",
        'extern "C++" {'
        + os.linesep
        + 'extern "C" int main() {'
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output(
        'extern "C++" {'
        + os.linesep
        + 'extern "C" int main(void) {'
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep
        + "}"
        + os.linesep,
        True,
    )

    # Don't match function calls
    test.add_input(
        "./Main.c",
        "int main() {"
        + os.linesep
        + "  foo();"
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output(
        "int main(void) {"
        + os.linesep
        + "  foo();"
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep,
        True,
    )

    # Don't match function calls with return (return is a keyword not a return
    # type)
    test.add_input(
        "./Main.c",
        "int main() {" + os.linesep + "  return foo();" + os.linesep + "}" + os.linesep,
    )
    test.add_output(
        "int main(void) {"
        + os.linesep
        + "  return foo();"
        + os.linesep
        + "}"
        + os.linesep,
        True,
    )

    # Match function prototypes
    test.add_input(
        "./Main.c",
        "int main();"
        + os.linesep
        + os.linesep
        + "int main() {"
        + os.linesep
        + "  foo();"
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output(
        "int main(void);"
        + os.linesep
        + os.linesep
        + "int main(void) {"
        + os.linesep
        + "  foo();"
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep,
        True,
    )

    # Make sure leaving extern block resets extern language type of
    # parent block
    test.add_input(
        "./Main.c",
        'extern "C++" {'
        + os.linesep
        + 'extern "C" int main() {'
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep
        + "int func() {"
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output(
        'extern "C++" {'
        + os.linesep
        + 'extern "C" int main(void) {'
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep
        + "int func() {"
        + os.linesep
        + "  return 0;"
        + os.linesep
        + "}"
        + os.linesep
        + "}"
        + os.linesep,
        True,
    )

    # Don't match lambda function that takes no arguments
    test.add_input(
        "./Main.cpp",
        'extern "C" {'
        + os.linesep
        + os.linesep
        + "HAL_Bool HAL_Initialize(int32_t timeout, int32_t mode) {"
        + os.linesep
        + "  std::atexit([]() {"
        + os.linesep
        + "    // Unregister our new data condition variable."
        + os.linesep
        + "  });"
        + os.linesep
        + "}"
        + os.linesep
        + os.linesep
        + '}  // extern "C"'
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Don't match a function call within a #ifdef
    test.add_input(
        "./Main.c",
        "ES_Event Elevator_Service_Run(ES_Event event) {"
        + os.linesep
        + "#ifdef USE_TATTLETALE"
        + os.linesep
        + "    ES_Tail(); // trace call stack end"
        + os.linesep
        + "#endif"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    test.add_input(
        "./Timer.hpp",
        'extern "C" void Timer1IntHandler();'
        + os.linesep
        + os.linesep
        + "class Timer {"
        + os.linesep
        + "public:"
        + os.linesep
        + "    void Set(uint32_t newTime);"
        + os.linesep
        + os.linesep
        + "    void Start();"
        + os.linesep
        + os.linesep
        + "    void Stop();"
        + os.linesep
        + os.linesep
        + "    uint16_t GetID() const;"
        + os.linesep
        + os.linesep
        + "    static uint32_t GetTime();"
        + os.linesep
        + os.linesep
        + "private:"
        + os.linesep
        + "    friend void Timer1IntHandler();"
        + os.linesep
        + "};"
        + os.linesep,
    )
    test.add_output(
        'extern "C" void Timer1IntHandler(void);'
        + os.linesep
        + os.linesep
        + "class Timer {"
        + os.linesep
        + "public:"
        + os.linesep
        + "    void Set(uint32_t newTime);"
        + os.linesep
        + os.linesep
        + "    void Start();"
        + os.linesep
        + os.linesep
        + "    void Stop();"
        + os.linesep
        + os.linesep
        + "    uint16_t GetID() const;"
        + os.linesep
        + os.linesep
        + "    static uint32_t GetTime();"
        + os.linesep
        + os.linesep
        + "private:"
        + os.linesep
        + "    friend void Timer1IntHandler();"
        + os.linesep
        + "};"
        + os.linesep,
        True,
    )

    # Ensure comments with } in them don't mess up brace stack
    test.add_input(
        "./Test.cpp",
        "void func() {" + os.linesep + "  // closing }" + os.linesep + "}" + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Ensure nested comments don't mess up brace stack
    test.add_input("./Test.cpp", "// { /* */ }" + os.linesep)
    test.add_latest_input_as_output(True)
    test.add_input("./Test.cpp", "{ // /* */ }" + os.linesep)
    test.add_latest_input_as_output(False)
    test.add_input("./Test.cpp", "{ /* // */ }" + os.linesep)
    test.add_latest_input_as_output(True)
    test.add_input("./Test.cpp", "{ /* */ // }" + os.linesep)
    test.add_latest_input_as_output(False)
    test.add_input("./Test.cpp", "{ // /* // */ }" + os.linesep)
    test.add_latest_input_as_output(False)

    # Ensure popping too many braces doesn't crash
    test.add_input("./Test.cpp", "}" + os.linesep)
    test.add_latest_input_as_output(False)

    # Ensure comments inside quoted string don't mess up brace stack
    test.add_input(
        "./Test.cpp",
        "void func() {"
        + os.linesep
        + '  // "//"'
        + os.linesep
        + '  if (!query.startswith("//")) {'
        + os.linesep
        + "    return;"
        + os.linesep
        + "  }"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Ensure braces in double quotes don't mess up brace stack
    test.add_input("./Test.cpp", "void func() { std::cout << '{'; }")
    test.add_latest_input_as_output(True)

    # Ensure braces in single quotes don't mess up brace stack
    test.add_input("./Test.cpp", 'void func() { std::cout << "{"; }')
    test.add_latest_input_as_output(True)

    # Ensure single quote within double quotes doesn't mess up brace stack
    test.add_input("./Test.cpp", 'void func() { std::cout << "\'"; }')
    test.add_latest_input_as_output(True)

    # Ensure double quote within single quotes doesn't mess up brace stack
    test.add_input("./Test.cpp", "void func() { std::cout << '\"'; }")
    test.add_latest_input_as_output(True)

    # Ensure escaped double quote doesn't mess up brace stack
    test.add_input("./Test.cpp", 'void func() { std::cout << "\\""; }')
    test.add_latest_input_as_output(True)

    # Ensure escaped single quote doesn't mess up brace stack
    test.add_input("./Test.cpp", "void func() { std::cout << '\\''; }")
    test.add_latest_input_as_output(True)

    # Ensure escaped backslash isn't considered as an escaped single quote
    test.add_input("./Test.cpp", "void func() { std::cout << '\\\\'; }")
    test.add_latest_input_as_output(True)

    # Ensure extern "C" match containing a linesep within a singleline comment
    # still ends the comment
    test.add_input(
        "./Test.cpp",
        'extern "C" {}  // extern "C"'
        + os.linesep
        + "namespace {"
        + os.linesep
        + "}  // namespace"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Ensure extern "C" with brace on next line gets matched
    test.add_input(
        "./Test.cpp",
        'extern "C"'
        + os.linesep
        + "{"
        + os.linesep
        + "  void func() {}"
        + os.linesep
        + '}  // extern "C"'
        + os.linesep,
    )
    test.add_output(
        'extern "C"'
        + os.linesep
        + "{"
        + os.linesep
        + "  void func(void) {}"
        + os.linesep
        + '}  // extern "C"'
        + os.linesep,
        True,
    )

    # Test logic for deduplicating braces within #ifdef
    test.add_input(
        "./Test.cpp",
        "void func() {"
        + os.linesep
        + "#ifdef _WIN32"
        + os.linesep
        + "  if (errno == WSAEWOULDBLOCK) {"
        + os.linesep
        + "#else"
        + os.linesep
        + "  if (errno == EWOULDBLOCK) {"
        + os.linesep
        + "#endif"
        + os.linesep
        + "  }"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Ensure extern "C" function with pointer return type gets matched
    test.add_input(
        "./Test.cpp",
        'extern "C" void* func() {}' + os.linesep,
    )
    test.add_output(
        'extern "C" void* func(void) {}' + os.linesep,
        True,
    )

    test.run(OutputType.FILE)
