from wpiformat.javaclass import JavaClass

from .test_tasktest import *


def test_javaclass():
    test = TaskTest(JavaClass())

    # No line separators at beginning of class
    test.add_input("./Test.java", "public class ExampleCommand extends Command {}\n")
    test.add_latest_input_as_output(True)

    # One line separator at beginning of class
    test.add_input(
        "./Test.java",
        """public class ExampleCommand extends Command {
  public ExampleCommand() {}
}
""",
    )
    test.add_latest_input_as_output(True)

    # Two line separators at beginning of class
    test.add_input(
        "./Test.java",
        """public class ExampleCommand extends Command {

  public ExampleCommand() {}
}
""",
    )
    test.add_output(
        """public class ExampleCommand extends Command {
  public ExampleCommand() {}
}
""",
        True,
    )

    # Three line separators at beginning of class
    test.add_input(
        "./Test.java",
        """public class ExampleCommand extends Command {


  public ExampleCommand() {}
}
""",
    )
    test.add_output(
        """public class ExampleCommand extends Command {
  public ExampleCommand() {}
}
""",
        True,
    )

    # class keyword in preceding comment to ensure regex matching it doesn't
    # continue past end of comment
    test.add_input(
        "./Test.java",
        """import edu.wpi.first.networktables.NetworkTableEntry;
import edu.wpi.first.wpilibj.Sendable;

/**
 * A helper class for Shuffleboard containers to handle common child operations.
 */
final class ContainerHelper {

  private final ShuffleboardContainer m_container;
""",
    )
    test.add_output(
        """import edu.wpi.first.networktables.NetworkTableEntry;
import edu.wpi.first.wpilibj.Sendable;

/**
 * A helper class for Shuffleboard containers to handle common child operations.
 */
final class ContainerHelper {
  private final ShuffleboardContainer m_container;
""",
        True,
    )

    test.run(OutputType.FILE)
