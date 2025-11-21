import subprocess
from pathlib import Path

from wpiformat.javaclass import JavaClass

from .test_tasktest import *


def test_javaclass():
    with OpenTemporaryDirectory():
        subprocess.run(["git", "init", "-q"])
        Path(".wpiformat").write_text("")

        test_java = Path("./Test.java").resolve()

        # No line separators at beginning of class
        run_and_check_file(
            JavaClass(),
            test_java,
            "public class ExampleCommand extends Command {}\n",
            "public class ExampleCommand extends Command {}\n",
            True,
        )

        # One line separator at beginning of class
        contents = """public class ExampleCommand extends Command {
  public ExampleCommand() {}
}
"""
        run_and_check_file(JavaClass(), test_java, contents, contents, True)

        # Two line separators at beginning of class
        run_and_check_file(
            JavaClass(),
            test_java,
            """public class ExampleCommand extends Command {

  public ExampleCommand() {}
}
""",
            """public class ExampleCommand extends Command {
  public ExampleCommand() {}
}
""",
            True,
        )

        # Three line separators at beginning of class
        run_and_check_file(
            JavaClass(),
            test_java,
            """public class ExampleCommand extends Command {


  public ExampleCommand() {}
}
""",
            """public class ExampleCommand extends Command {
  public ExampleCommand() {}
}
""",
            True,
        )

        # class keyword in preceding comment to ensure regex matching it doesn't
        # continue past end of comment
        run_and_check_file(
            JavaClass(),
            test_java,
            """import edu.wpi.first.networktables.NetworkTableEntry;
import edu.wpi.first.wpilibj.Sendable;

/**
 * A helper class for Shuffleboard containers to handle common child operations.
 */
final class ContainerHelper {

  private final ShuffleboardContainer m_container;
""",
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
