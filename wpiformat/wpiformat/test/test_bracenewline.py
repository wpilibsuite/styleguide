import os

from .tasktest import *
from wpiformat.bracenewline import BraceNewline


def test_bracenewline():
    test = TaskTest(BraceNewline())

    # Brackets on same line
    test.add_input("./Test.cpp",
        "void func1() {}" + os.linesep + \
        "void func2() {}" + os.linesep)
    test.add_output(
        "void func1() {}" + os.linesep + \
        os.linesep + \
        "void func2() {}" + os.linesep, True, True)

    # Brackets on next line
    test.add_input("./Test.cpp",
        "void func1() {" + os.linesep + \
        "}" + os.linesep + \
        "void func2() {" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "void func1() {" + os.linesep + \
        "}" + os.linesep + \
        os.linesep + \
        "void func2() {" + os.linesep + \
        "}" + os.linesep, True, True)

    # Comments after brackets
    test.add_input("./Test.cpp",
        "void func1() {" + os.linesep + \
        "}  // This is a comment" + os.linesep + \
        "void func2() {" + os.linesep + \
        "}  /* This is a comment */" + os.linesep + \
        "void func3() {" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "void func1() {" + os.linesep + \
        "}  // This is a comment" + os.linesep + \
        os.linesep + \
        "void func2() {" + os.linesep + \
        "}  /* This is a comment */" + os.linesep + \
        os.linesep + \
        "void func3() {" + os.linesep + \
        "}" + os.linesep, True, True)

    # Don't add line separators to uncondensed if statements (after last brace
    # is OK)
    test.add_input("./Test.cpp",
        "void func1() {" + os.linesep + \
        "  if (1) {" + os.linesep + \
        "  }" + os.linesep + \
        "  else {" + os.linesep + \
        "  }" + os.linesep + \
        "}" + os.linesep)
    test.add_latest_input_as_output(True)

    # Don't add line separators to condensed if statements (after last brace
    # is OK)
    test.add_input("./Test.cpp",
        "void func1() {" + os.linesep + \
        "  if (1) {" + os.linesep + \
        "  } else if () {" + os.linesep + \
        "  } else {" + os.linesep + \
        "    // comment" + os.linesep + \
        "  }" + os.linesep + \
        "}" + os.linesep)
    test.add_latest_input_as_output(True)

    # Don't add line separators before #endif statements
    test.add_input("./Main.cpp",
        "using decay_t = typename decay<T>::type;" + os.linesep + \
        "}  // namespace std" + os.linesep + \
        "#endif" + os.linesep)
    test.add_latest_input_as_output(True)

    # Don't insert line separators within multiline comments
    test.add_input("./Main.java",
        "/* to fine tune the pid loop." + os.linesep + \
        " *"  + os.linesep + \
        " * @return the {@link PIDController} used by this {@link PIDSubsystem}" + os.linesep + \
        " */" + os.linesep + \
        "public PIDController getPIDController() {" + os.linesep)
    test.add_latest_input_as_output(True)

    # Don't insert line separators within single line comments
    test.add_input("./Main.java",
        "// @return the {@link PIDController} used by this {@link PIDSubsystem}" + os.linesep + \
        "public PIDController getPIDController() {" + os.linesep)
    test.add_latest_input_as_output(True)

    test.run(OutputType.FILE)
