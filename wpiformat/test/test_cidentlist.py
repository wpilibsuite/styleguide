import os

from wpiformat.config import Config
from wpiformat.cidentlist import CIdentList


def test_cidentlist():
    task = CIdentList()

    inputs = []
    outputs = []

    # Main.cpp: signature for C++ function
    inputs.append(("./Main.cpp",
        "int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    # Main.cpp: signature for C function in extern "C" block
    inputs.append(("./Main.cpp",
        "extern \"C\" {" + os.linesep + \
        "int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "extern \"C\" {" + os.linesep + \
        "int main(void) {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep, True, True))

    # Main.cpp: signature for C function marked extern "C"
    inputs.append(("./Main.cpp",
        "extern \"C\" int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "extern \"C\" int main(void) {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep, True, True))

    # Main.cpp: extern "C++" function nested in extern "C" block
    inputs.append(("./Main.cpp",
        "extern \"C\" {" + os.linesep + \
        "extern \"C++\" int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    # Main.c: signature for C function
    inputs.append(("./Main.c",
        "int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "int main(void) {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep, True, True))

    # Main.c: signature for C++ function in extern "C++" block
    inputs.append(("./Main.c",
        "extern \"C++\" {" + os.linesep + \
        "int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    # Main.c: signature for C++ function marked extern "C++"
    inputs.append(("./Main.c",
        "extern \"C++\" int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    # Main.c: extern "C" function nested in extern "C++" block
    inputs.append(("./Main.c",
        "extern \"C++\" {" + os.linesep + \
        "extern \"C\" int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "extern \"C++\" {" + os.linesep + \
        "extern \"C\" int main(void) {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep, True, True))

    # Don't match function calls
    inputs.append(("./Main.c",
        "int main() {" + os.linesep + \
        "  foo();" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "int main(void) {" + os.linesep + \
        "  foo();" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep, True, True))

    # Don't match function calls with return (return is a keyword not a return
    # type)
    inputs.append(("./Main.c",
        "int main() {" + os.linesep + \
        "  return foo();" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "int main(void) {" + os.linesep + \
        "  return foo();" + os.linesep + \
        "}" + os.linesep, True, True))

    # Match function prototypes
    inputs.append(("./Main.c",
        "int main();" + os.linesep + \
        os.linesep + \
        "int main() {" + os.linesep + \
        "  foo();" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "int main(void);" + os.linesep + \
        os.linesep + \
        "int main(void) {" + os.linesep + \
        "  foo();" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep, True, True))

    # Make sure leaving extern block resets extern language type of
    # parent block
    inputs.append(("./Main.c",
        "extern \"C++\" {" + os.linesep + \
        "extern \"C\" int main() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "int func() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "extern \"C++\" {" + os.linesep + \
        "extern \"C\" int main(void) {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "int func() {" + os.linesep + \
        "  return 0;" + os.linesep + \
        "}" + os.linesep + \
        "}" + os.linesep, True, True))

    # Don't match lambda function that takes no arguments
    inputs.append(("./Main.cpp",
        "extern \"C\" {" + os.linesep + \
        os.linesep + \
        "HAL_Bool HAL_Initialize(int32_t timeout, int32_t mode) {" + os.linesep + \
        "  std::atexit([]() {" + os.linesep + \
        "    // Unregister our new data condition variable." + os.linesep + \
        "  });" + os.linesep + \
        "}" + os.linesep + \
        os.linesep + \
        "}  // extern \"C\"" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    # Don't match a function call within a #ifdef
    inputs.append(("./Main.c",
        "ES_Event Elevator_Service_Run(ES_Event event) {" + os.linesep + \
        "#ifdef USE_TATTLETALE" + os.linesep + \
        "    ES_Tail(); // trace call stack end" + os.linesep + \
        "#endif" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    inputs.append(("./Timer.hpp",
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
        "};" + os.linesep))
    outputs.append((
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
        "};" + os.linesep, True, True))

    assert len(inputs) == len(outputs)

    config_file = Config(os.path.abspath(os.getcwd()), ".styleguide")
    for i in range(len(inputs)):
        output, file_changed, success = task.run_pipeline(
            config_file, inputs[i][0], inputs[i][1])
        assert output == outputs[i][0]
        assert file_changed == outputs[i][1]
        assert success == outputs[i][2]
