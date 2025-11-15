from wpiformat.cidentlist import CIdentList

from .test_tasktest import *


def test_cidentlist():
    # Main.cpp: signature for C++ function
    contents = """int main() {
  return 0;
}
"""
    run_and_check_file(CIdentList(), "./Main.cpp", contents, contents, True)

    # Main.cpp: signature for C function in extern "C" block
    run_and_check_file(
        CIdentList(),
        "./Main.cpp",
        """extern "C" {
int main() {
  return 0;
}
}
""",
        """extern "C" {
int main(void) {
  return 0;
}
}
""",
        True,
    )

    # Main.cpp: signature for C function marked extern "C"
    run_and_check_file(
        CIdentList(),
        "./Main.cpp",
        """extern "C" int main() {
  return 0;
}
""",
        """extern "C" int main(void) {
  return 0;
}
""",
        True,
    )

    # Main.cpp: extern "C++" function in extern "C" block
    contents = """extern "C" {
extern "C++" int main() {
  return 0;
}
}
"""
    run_and_check_file(CIdentList(), "./Main.cpp", contents, contents, True)

    # Main.c: signature for C function
    run_and_check_file(
        CIdentList(),
        "./Main.c",
        """int main() {
  return 0;
}
""",
        """int main(void) {
  return 0;
}
""",
        True,
    )

    # Main.c: signature for C++ function in extern "C++" block
    contents = """extern "C++" {
int main() {
  return 0;
}
}
"""
    run_and_check_file(CIdentList(), "./Main.c", contents, contents, True)

    # Main.c: signature for C++ function marked extern "C++"
    contents = """extern "C++" int main() {
  return 0;
}
"""
    run_and_check_file(CIdentList(), "./Main.c", contents, contents, True)

    # Main.c: extern "C" function nested in extern "C++" block
    run_and_check_file(
        CIdentList(),
        "./Main.c",
        """extern "C++" {
extern "C" int main() {
  return 0;
}
}
""",
        """extern "C++" {
extern "C" int main(void) {
  return 0;
}
}
""",
        True,
    )

    # Don't match function calls
    run_and_check_file(
        CIdentList(),
        "./Main.c",
        """int main() {
  foo();
  return 0;
}
""",
        """int main(void) {
  foo();
  return 0;
}
""",
        True,
    )

    # Don't match function calls with return (return is a keyword not a return
    # type)
    run_and_check_file(
        CIdentList(),
        "./Main.c",
        """int main() {
  return foo();
}
""",
        """int main(void) {
  return foo();
}
""",
        True,
    )

    # Match function prototypes
    run_and_check_file(
        CIdentList(),
        "./Main.c",
        """int main();

int main() {
  foo();
  return 0;
}
""",
        """int main(void);

int main(void) {
  foo();
  return 0;
}
""",
        True,
    )

    # Make sure leaving extern block resets extern language type of parent block
    run_and_check_file(
        CIdentList(),
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
    contents = """extern "C" {

HAL_Bool HAL_Initialize(int32_t timeout, int32_t mode) {
  std::atexit([]() {
    // Unregister our new data condition variable.
  });
}

}  // extern "C"
"""
    run_and_check_file(CIdentList(), "./Main.cpp", contents, contents, True)

    # Don't match a function call within a #ifdef
    contents = """ES_Event Elevator_Service_Run(ES_Event event) {
#ifdef USE_TATTLETALE
    ES_Tail(); // trace call stack end
#endif
}
"""
    run_and_check_file(CIdentList(), "./Main.c", contents, contents, True)

    run_and_check_file(
        CIdentList(),
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
    contents = """void func() {
  // closing }
}
"""
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)

    # Ensure nested comments don't mess up brace stack
    contents = "// { /* */ }\n"
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)
    contents = "{ // /* */ }\n"
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, False)
    contents = "{ /* // */ }\n"
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)
    contents = "{ /* */ // }\n"
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, False)
    contents = "{ // /* // */ }\n"
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, False)

    # Ensure popping too many braces doesn't crash
    run_and_check_file(CIdentList(), "./Test.cpp", "}\n", "}\n", False)

    # Ensure comments inside quoted string don't mess up brace stack
    contents = """void func() {
  // "//"
  if (!query.startswith("//")) {
    return;
  }
}
"""
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)

    # Ensure braces in double quotes don't mess up brace stack
    contents = "void func() { std::cout << '{'; }"
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)

    # Ensure braces in single quotes don't mess up brace stack
    contents = 'void func() { std::cout << "{"; }'
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)

    # Ensure single quote within double quotes doesn't mess up brace stack
    contents = 'void func() { std::cout << "\'"; }'
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)

    # Ensure double quote within single quotes doesn't mess up brace stack
    contents = "void func() { std::cout << '\"'; }"
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)

    # Ensure escaped double quote doesn't mess up brace stack
    contents = 'void func() { std::cout << "\\""; }'
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)

    # Ensure escaped single quote doesn't mess up brace stack
    contents = "void func() { std::cout << '\\''; }"
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)

    # Ensure escaped backslash isn't considered as an escaped single quote
    contents = "void func() { std::cout << '\\\\'; }"
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)

    # Ensure extern "C" match containing a linesep within a singleline comment
    # still ends the comment
    contents = """extern "C" {}  // extern "C"
namespace {
}  // namespace
"""
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)

    # Ensure extern "C" with brace on next line gets matched
    run_and_check_file(
        CIdentList(),
        "./Test.cpp",
        """extern "C"
{
  void func() {}
}  // extern "C"
""",
        """extern "C"
{
  void func(void) {}
}  // extern "C"
""",
        True,
    )

    # Test logic for deduplicating braces within #ifdef
    contents = """void func() {
#ifdef _WIN32
  if (errno == WSAEWOULDBLOCK) {
#else
  if (errno == EWOULDBLOCK) {
#endif
  }
}
"""
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)

    # Ensure extern "C" function with pointer return type gets matched
    run_and_check_file(
        CIdentList(),
        "./Test.cpp",
        'extern "C" void* func() {}\n',
        'extern "C" void* func(void) {}\n',
        True,
    )

    # Ensure single quotes in numeric literals are ignored
    contents = "void func() { int x = 1'000; }"
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)

    # Ensure single quotes in hexadecimal literals are ignored
    contents = "void func() { int x = 0xffff'ffff; }"
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)

    # Ensure single quotes after numeric literals are not ignored
    contents = "void func() { std::cout << 1 << '0'; }"
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)

    # Ensure single quotes after hexadecimal characters are not ignored
    contents = "void func() { std::cout << 1 << 'a'; }"
    run_and_check_file(CIdentList(), "./Test.cpp", contents, contents, True)
