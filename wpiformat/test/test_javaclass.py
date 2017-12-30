import os

from wpiformat.config import Config
from wpiformat.javaclass import JavaClass


def test_javaclass():
    task = JavaClass()

    inputs = []
    outputs = []

    # No line separators at beginning of class
    inputs.append(
        ("./Test.java",
         "public class ExampleCommand extends Command {}" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    # One line separator at beginning of class
    inputs.append(("./Test.java",
        "public class ExampleCommand extends Command {" + os.linesep + \
        "  public ExampleCommand() {}" + os.linesep + \
        "}" + os.linesep))
    outputs.append((inputs[len(inputs) - 1][1], False, True))

    # Two line separators at beginning of class
    inputs.append(("./Test.java",
        "public class ExampleCommand extends Command {" + os.linesep + \
        os.linesep + \
        "  public ExampleCommand() {}" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "public class ExampleCommand extends Command {" + os.linesep + \
        "  public ExampleCommand() {}" + os.linesep + \
        "}" + os.linesep, True, True))

    # Three line separators at beginning of class
    inputs.append(("./Test.java",
        "public class ExampleCommand extends Command {" + os.linesep + \
        os.linesep + \
        os.linesep + \
        "  public ExampleCommand() {}" + os.linesep + \
        "}" + os.linesep))
    outputs.append((
        "public class ExampleCommand extends Command {" + os.linesep + \
        "  public ExampleCommand() {}" + os.linesep + \
        "}" + os.linesep, True, True))

    assert len(inputs) == len(outputs)

    config_file = Config(os.path.abspath(os.getcwd()), ".styleguide")
    for i in range(len(inputs)):
        output, file_changed, success = task.run_pipeline(
            config_file, inputs[i][0], inputs[i][1])
        assert output == outputs[i][0]
        assert file_changed == outputs[i][1]
        assert success == outputs[i][2]
