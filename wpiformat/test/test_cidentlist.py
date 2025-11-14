from wpiformat.cidentlist import CIdentList

from .test_tasktest import *


def test_cidentlist():
    test = TaskTest(CIdentList())

    # Main.cpp: signature for C++ function
    test.add_input(
        "./Main.cpp",
        """int main() {
  return 0;
}
""",
    )
    test.add_latest_input_as_output(True)

    # Main.cpp: signature for C function in extern "C" block
    test.add_input(
        "./Main.cpp",
        """extern "C" {
int main() {
  return 0;
}
}
""",
    )
    test.add_output(
        """extern "C" {
int main(void) {
  return 0;
}
}
""",
        True,
    )

    # Main.cpp: signature for C function marked extern "C"
    test.add_input(
        "./Main.cpp",
        """extern "C" int main() {
  return 0;
}
""",
    )
    test.add_output(
        """extern "C" int main(void) {
  return 0;
}
""",
        True,
    )

    # Main.cpp: extern "C++" function nested in extern "C" block
    test.add_input(
        "./Main.cpp",
        """extern "C" {
extern "C++" int main() {
  return 0;
}
}
""",
    )
    test.add_latest_input_as_output(True)

    # Main.c: signature for C function
    test.add_input(
        "./Main.c",
        """int main() {
  return 0;
}
""",
    )
    test.add_output(
        """int main(void) {
  return 0;
}
""",
        True,
    )

    # Main.c: signature for C++ function in extern "C++" block
    test.add_input(
        "./Main.c",
        """extern "C++" {
int main() {
  return 0;
}
}
""",
    )
    test.add_latest_input_as_output(True)

    # Main.c: signature for C++ function marked extern "C++"
    test.add_input(
        "./Main.c",
        """extern "C++" int main() {
  return 0;
}
""",
    )
    test.add_latest_input_as_output(True)

    # Main.c: extern "C" function nested in extern "C++" block
    test.add_input(
        "./Main.c",
        """extern "C++" {
extern "C" int main() {
  return 0;
}
}
""",
    )
    test.add_output(
        """extern "C++" {
extern "C" int main(void) {
  return 0;
}
}
""",
        True,
    )

    # Don't match function calls
    test.add_input(
        "./Main.c",
        """int main() {
  foo();
  return 0;
}
""",
    )
    test.add_output(
        """int main(void) {
  foo();
  return 0;
}
""",
        True,
    )

    # Don't match function calls with return (return is a keyword not a return
    # type)
    test.add_input(
        "./Main.c",
        """int main() {
  return foo();
}
""",
    )
    test.add_output(
        """int main(void) {
  return foo();
}
""",
        True,
    )

    # Match function prototypes
    test.add_input(
        "./Main.c",
        """int main();

int main() {
  foo();
  return 0;
}
""",
    )
    test.add_output(
        """int main(void);

int main(void) {
  foo();
  return 0;
}
""",
        True,
    )

    # Make sure leaving extern block resets extern language type of
    # parent block
    test.add_input(
        "./Main.c",
        """extern "C++" {
extern "C" int main() {
  return 0;
}
int func() {
  return 0;
}
}
""",
    )
    test.add_output(
        """extern "C++" {
extern "C" int main(void) {
  return 0;
}
int func() {
  return 0;
}
}
""",
        True,
    )

    # Don't match lambda function that takes no arguments
    test.add_input(
        "./Main.cpp",
        """extern "C" {

HAL_Bool HAL_Initialize(int32_t timeout, int32_t mode) {
  std::atexit([]() {
    // Unregister our new data condition variable.
  });
}

}  // extern "C"
""",
    )
    test.add_latest_input_as_output(True)

    # Don't match a function call within a #ifdef
    test.add_input(
        "./Main.c",
        """ES_Event Elevator_Service_Run(ES_Event event) {
#ifdef USE_TATTLETALE
    ES_Tail(); // trace call stack end
#endif
}
""",
    )
    test.add_latest_input_as_output(True)

    test.add_input(
        "./Timer.hpp",
        """extern "C" void Timer1IntHandler();

class Timer {
public:
    void Set(uint32_t newTime);

    void Start();

    void Stop();

    uint16_t GetID() const;

    static uint32_t GetTime();

private:
    friend void Timer1IntHandler();
};
""",
    )
    test.add_output(
        """extern "C" void Timer1IntHandler(void);

class Timer {
public:
    void Set(uint32_t newTime);

    void Start();

    void Stop();

    uint16_t GetID() const;

    static uint32_t GetTime();

private:
    friend void Timer1IntHandler();
};
""",
        True,
    )

    # Ensure comments with } in them don't mess up brace stack
    test.add_input(
        "./Test.cpp",
        """void func() {
  // closing }
}
""",
    )
    test.add_latest_input_as_output(True)

    # Ensure nested comments don't mess up brace stack
    test.add_input("./Test.cpp", "// { /* */ }\n")
    test.add_latest_input_as_output(True)
    test.add_input("./Test.cpp", "{ // /* */ }\n")
    test.add_latest_input_as_output(False)
    test.add_input("./Test.cpp", "{ /* // */ }\n")
    test.add_latest_input_as_output(True)
    test.add_input("./Test.cpp", "{ /* */ // }\n")
    test.add_latest_input_as_output(False)
    test.add_input("./Test.cpp", "{ // /* // */ }\n")
    test.add_latest_input_as_output(False)

    # Ensure popping too many braces doesn't crash
    test.add_input("./Test.cpp", "}\n")
    test.add_latest_input_as_output(False)

    # Ensure comments inside quoted string don't mess up brace stack
    test.add_input(
        "./Test.cpp",
        """void func() {
  // "//"
  if (!query.startswith("//")) {
    return;
  }
}
""",
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
        """extern "C" {}  // extern "C"
namespace {
}  // namespace
""",
    )
    test.add_latest_input_as_output(True)

    # Ensure extern "C" with brace on next line gets matched
    test.add_input(
        "./Test.cpp",
        """extern "C"
{
  void func() {}
}  // extern "C"
""",
    )
    test.add_output(
        """extern "C"
{
  void func(void) {}
}  // extern "C"
""",
        True,
    )

    # Test logic for deduplicating braces within #ifdef
    test.add_input(
        "./Test.cpp",
        """void func() {
#ifdef _WIN32
  if (errno == WSAEWOULDBLOCK) {
#else
  if (errno == EWOULDBLOCK) {
#endif
  }
}
""",
    )
    test.add_latest_input_as_output(True)

    # Ensure extern "C" function with pointer return type gets matched
    test.add_input(
        "./Test.cpp",
        'extern "C" void* func() {}\n',
    )
    test.add_output(
        'extern "C" void* func(void) {}\n',
        True,
    )

    # Ensure single quotes in numeric literals are ignored
    test.add_input("./Test.cpp", "void func() { int x = 1'000; }")
    test.add_latest_input_as_output(True)

    # Ensure single quotes in hexadecimal literals are ignored
    test.add_input("./Test.cpp", "void func() { int x = 0xffff'ffff; }")
    test.add_latest_input_as_output(True)

    # Ensure single quotes after numeric literals are not ignored
    test.add_input("./Test.cpp", "void func() { std::cout << 1 << '0'; }")
    test.add_latest_input_as_output(True)

    # Ensure single quotes after hexadecimal characters are not ignored
    test.add_input("./Test.cpp", "void func() { std::cout << 1 << 'a'; }")
    test.add_latest_input_as_output(True)

    test.run(OutputType.FILE)
