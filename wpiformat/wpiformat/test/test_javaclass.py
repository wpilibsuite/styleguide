import os

from .test_tasktest import *
from wpiformat.javaclass import JavaClass


def test_javaclass():
    test = TaskTest(JavaClass())

    # No line separators at beginning of class
    test.add_input(
        "./Test.java", "public class ExampleCommand extends Command {}" + os.linesep
    )
    test.add_latest_input_as_output(True)

    # One line separator at beginning of class
    test.add_input(
        "./Test.java",
        "public class ExampleCommand extends Command {"
        + os.linesep
        + "  public ExampleCommand() {}"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Two line separators at beginning of class
    test.add_input(
        "./Test.java",
        "public class ExampleCommand extends Command {"
        + os.linesep
        + os.linesep
        + "  public ExampleCommand() {}"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output(
        "public class ExampleCommand extends Command {"
        + os.linesep
        + "  public ExampleCommand() {}"
        + os.linesep
        + "}"
        + os.linesep,
        True,
    )

    # Three line separators at beginning of class
    test.add_input(
        "./Test.java",
        "public class ExampleCommand extends Command {"
        + os.linesep
        + os.linesep
        + os.linesep
        + "  public ExampleCommand() {}"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output(
        "public class ExampleCommand extends Command {"
        + os.linesep
        + "  public ExampleCommand() {}"
        + os.linesep
        + "}"
        + os.linesep,
        True,
    )

    # class keyword in preceding comment to ensure regex matching it doesn't
    # continue past end of comment
    test.add_input(
        "./Test.java",
        "import edu.wpi.first.networktables.NetworkTableEntry;"
        + os.linesep
        + "import edu.wpi.first.wpilibj.Sendable;"
        + os.linesep
        + os.linesep
        + "/**"
        + os.linesep
        + " * A helper class for Shuffleboard containers to handle common child operations."
        + os.linesep
        + " */"
        + os.linesep
        + "final class ContainerHelper {"
        + os.linesep
        + os.linesep
        + "  private final ShuffleboardContainer m_container;"
        + os.linesep,
    )
    test.add_output(
        "import edu.wpi.first.networktables.NetworkTableEntry;"
        + os.linesep
        + "import edu.wpi.first.wpilibj.Sendable;"
        + os.linesep
        + os.linesep
        + "/**"
        + os.linesep
        + " * A helper class for Shuffleboard containers to handle common child operations."
        + os.linesep
        + " */"
        + os.linesep
        + "final class ContainerHelper {"
        + os.linesep
        + "  private final ShuffleboardContainer m_container;"
        + os.linesep,
        True,
    )

    test.run(OutputType.FILE)
