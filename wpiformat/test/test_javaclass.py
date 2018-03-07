import os

from test.tasktest import *
from wpiformat.javaclass import JavaClass


def test_javaclass():
    test = TaskTest(JavaClass())

    # No line separators at beginning of class
    test.add_input(
        "./Test.java",
        "public class ExampleCommand extends Command {}" + os.linesep)
    test.add_latest_input_as_output(True)

    # One line separator at beginning of class
    test.add_input("./Test.java",
        "public class ExampleCommand extends Command {" + os.linesep + \
        "  public ExampleCommand() {}" + os.linesep + \
        "}" + os.linesep)
    test.add_latest_input_as_output(True)

    # Two line separators at beginning of class
    test.add_input("./Test.java",
        "public class ExampleCommand extends Command {" + os.linesep + \
        os.linesep + \
        "  public ExampleCommand() {}" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "public class ExampleCommand extends Command {" + os.linesep + \
        "  public ExampleCommand() {}" + os.linesep + \
        "}" + os.linesep, True, True)

    # Three line separators at beginning of class
    test.add_input("./Test.java",
        "public class ExampleCommand extends Command {" + os.linesep + \
        os.linesep + \
        os.linesep + \
        "  public ExampleCommand() {}" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "public class ExampleCommand extends Command {" + os.linesep + \
        "  public ExampleCommand() {}" + os.linesep + \
        "}" + os.linesep, True, True)

    test.run(OutputType.FILE)
