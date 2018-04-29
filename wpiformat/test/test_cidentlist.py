import os

from test.tasktest import *
from wpiformat.cidentlist import CIdentList


def test_cidentlist():
    test = TaskTest(CIdentList())

    # Main.cpp: signature for C++ function
    test.add_input("./Main.cpp",
        "int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep)
    test.add_latest_input_as_output(True)

    # Main.cpp: signature for C function in extern "C" block
    test.add_input("./Main.cpp",
        "extern \"C\" {" + os.linesep + \
        "int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "extern \"C\" {" + os.linesep + \
        "int main(void) {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep, True, True)

    # Main.cpp: signature for C function marked extern "C"
    test.add_input("./Main.cpp",
        "extern \"C\" int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "extern \"C\" int main(void) {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep, True, True)

    # Main.cpp: extern "C++" function nested in extern "C" block
    test.add_input("./Main.cpp",
        "extern \"C\" {" + os.linesep + \
        "extern \"C++\" int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep)
    test.add_latest_input_as_output(True)

    # Main.c: signature for C function
    test.add_input("./Main.c",
        "int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "int main(void) {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep, True, True)

    # Main.c: signature for C++ function in extern "C++" block
    test.add_input("./Main.c",
        "extern \"C++\" {" + os.linesep + \
        "int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep)
    test.add_latest_input_as_output(True)

    # Main.c: signature for C++ function marked extern "C++"
    test.add_input("./Main.c",
        "extern \"C++\" int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep)
    test.add_latest_input_as_output(True)

    # Main.c: extern "C" function nested in extern "C++" block
    test.add_input("./Main.c",
        "extern \"C++\" {" + os.linesep + \
        "extern \"C\" int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "extern \"C++\" {" + os.linesep + \
        "extern \"C\" int main(void) {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep, True, True)

    # Don't match function calls
    test.add_input("./Main.c",
        "int main() {" + os.linesep + \
        "  foo();" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "int main(void) {" + os.linesep + \
        "  foo();" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep, True, True)

    # Don't match function calls with return (return is a keyword not a return
    # type)
    test.add_input("./Main.c",
        "int main() {" + os.linesep + \
        "  return foo();" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "int main(void) {" + os.linesep + \
        "  return foo();" + os.linesep + \
        "}" + os.linesep, True, True)

    # Match function prototypes
    test.add_input("./Main.c",
        "int main();" + os.linesep + \
        os.linesep + \
        "int main() {" + os.linesep + \
        "  foo();" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "int main(void);" + os.linesep + \
        os.linesep + \
        "int main(void) {" + os.linesep + \
        "  foo();" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep, True, True)

    # Make sure leaving extern block resets extern language type of
    # parent block
    test.add_input("./Main.c",
        "extern \"C++\" {" + os.linesep + \
        "extern \"C\" int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "int func() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "extern \"C++\" {" + os.linesep + \
        "extern \"C\" int main(void) {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "int func() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep, True, True)

    # Don't match lambda function that takes no arguments
    test.add_input("./Main.cpp",
        "extern \"C\" {" + os.linesep + \
        os.linesep + \
        "HAL_Bool HAL_Initialize(int32_t timeout, int32_t mode) {" + os.linesep + \
        "  std::atexit([]() {" + os.linesep + \
        "    // Unregister our new data condition variable." + os.linesep + \
        "  });" + os.linesep + \
        "}" + os.linesep + \
        os.linesep + \
        "}  // extern \"C\"" + os.linesep)
    test.add_latest_input_as_output(True)

    # Don't match a function call within a #ifdef
    test.add_input("./Main.c",
        "ES_Event Elevator_Service_Run(ES_Event event) {" + os.linesep + \
        "#ifdef USE_TATTLETALE" + os.linesep + \
        "    ES_Tail(); // trace call stack end" + os.linesep + \
        "#endif" + os.linesep)
    test.add_latest_input_as_output(True)

    test.add_input("./Timer.hpp",
        "extern \"C\" void Timer1IntHandler();" + os.linesep + \
        os.linesep + \
        "class Timer {" + os.linesep + \
        "public:" + os.linesep + \
        "    void Set(uint32_t newTime);" + os.linesep + \
        os.linesep + \
        "    void Start();" + os.linesep + \
        os.linesep + \
        "    void Stop();" + os.linesep + \
        os.linesep + \
        "    uint16_t GetID() const;" + os.linesep + \
        os.linesep + \
        "    static uint32_t GetTime();" + os.linesep + \
        os.linesep + \
        "private:" + os.linesep + \
        "    friend void Timer1IntHandler();" + os.linesep + \
        "};" + os.linesep)
    test.add_output(
        "extern \"C\" void Timer1IntHandler(void);" + os.linesep + \
        os.linesep + \
        "class Timer {" + os.linesep + \
        "public:" + os.linesep + \
        "    void Set(uint32_t newTime);" + os.linesep + \
        os.linesep + \
        "    void Start();" + os.linesep + \
        os.linesep + \
        "    void Stop();" + os.linesep + \
        os.linesep + \
        "    uint16_t GetID() const;" + os.linesep + \
        os.linesep + \
        "    static uint32_t GetTime();" + os.linesep + \
        os.linesep + \
        "private:" + os.linesep + \
        "    friend void Timer1IntHandler();" + os.linesep + \
        "};" + os.linesep, True, True)

    # Ensure comments with } in them don't mess up brace stack
    test.add_input("./Test.cpp",
        "void func() {" + os.linesep + \
        "  // closing }" + os.linesep + \
        "}" + os.linesep)
    test.add_latest_input_as_output(True)

    test.run(OutputType.FILE)
