import os

from .test_tasktest import *
from wpiformat.commentformat import CommentFormat


def test_commentformat():
    test = TaskTest(CommentFormat())

    # Empty comment
    test.add_input("./Test.h", "/**" + os.linesep + " */" + os.linesep)
    test.add_latest_input_as_output(True)

    # Adds space before asterisks
    test.add_input(
        "./Test.h", "/**" + os.linesep + "*" + os.linesep + "*/" + os.linesep
    )
    test.add_output("/**" + os.linesep + " */" + os.linesep, True)

    # Put /** on separate line
    test.add_input("./Test.h", "/** asdf */" + os.linesep)
    test.add_output(
        "/**" + os.linesep + " * Asdf." + os.linesep + " */" + os.linesep, True
    )

    # Paragraphs but no tags
    test.add_input(
        "./Accelerometer.cpp",
        "/**"
        + os.linesep
        + " * Get the x-axis acceleration"
        + os.linesep
        + " *"
        + os.linesep
        + " * This is a floating point value in units of 1 g-force"
        + os.linesep
        + " */"
        + os.linesep,
    )
    test.add_output(
        "/**"
        + os.linesep
        + " * Get the x-axis acceleration."
        + os.linesep
        + " *"
        + os.linesep
        + " * This is a floating point value in units of 1 g-force."
        + os.linesep
        + " */"
        + os.linesep,
        True,
    )

    # Paragraphs but no tags
    test.add_input(
        "./Accelerometer.cpp",
        "/**"
        + os.linesep
        + " * Convert a 12-bit raw acceleration value into a scaled double in units of"
        + os.linesep
        + " * 1 g-force, taking into account the accelerometer range."
        + os.linesep
        + " */"
        + os.linesep,
    )
    test.add_output(
        "/**"
        + os.linesep
        + " * Convert a 12-bit raw acceleration value into a scaled double in units of 1"
        + os.linesep
        + " * g-force, taking into account the accelerometer range."
        + os.linesep
        + " */"
        + os.linesep,
        True,
    )

    # @param tag but with blank line before it and no description
    test.add_input(
        "./AnalogInput.cpp",
        "/**"
        + os.linesep
        + " *"
        + os.linesep
        + " * @param analogPortHandle Handle to the analog port."
        + os.linesep
        + " */"
        + os.linesep,
    )
    test.add_output(
        "/**"
        + os.linesep
        + " * @param analogPortHandle Handle to the analog port."
        + os.linesep
        + " */"
        + os.linesep,
        True,
    )

    # Paragraph with @param and @return tags
    test.add_input(
        "./AnalogAccumulator.cpp",
        "/**"
        + os.linesep
        + " * Is the channel attached to an accumulator."
        + os.linesep
        + " *"
        + os.linesep
        + " * @param analogPortHandle Handle to the analog port."
        + os.linesep
        + " * @return The analog channel is attached to an accumulator."
        + os.linesep
        + " */"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Paragraph and @return with no empty line between them
    test.add_input(
        "./AnalogTrigger.cpp",
        "/**"
        + os.linesep
        + " * Return the InWindow output of the analog trigger."
        + os.linesep
        + " *"
        + os.linesep
        + " * True if the analog input is between the upper and lower limits."
        + os.linesep
        + " * @return The InWindow output of the analog trigger."
        + os.linesep
        + " */"
        + os.linesep,
    )
    test.add_output(
        "/**"
        + os.linesep
        + " * Return the InWindow output of the analog trigger."
        + os.linesep
        + " *"
        + os.linesep
        + " * True if the analog input is between the upper and lower limits."
        + os.linesep
        + " *"
        + os.linesep
        + " * @return The InWindow output of the analog trigger."
        + os.linesep
        + " */"
        + os.linesep,
        True,
    )

    # C++: paragraphs with @param tags
    test.add_input(
        "./PIDController.cpp",
        "  /**"
        + os.linesep
        + "   * Allocate a PID object with the given constants for P, I, D."
        + os.linesep
        + "   *"
        + os.linesep
        + "   * More summary."
        + os.linesep
        + "   * Even more summary."
        + os.linesep
        + "   *"
        + os.linesep
        + "   * @param Kp the proportional coefficient"
        + os.linesep
        + "   * @param Ki the integral coefficient"
        + os.linesep
        + "   * @param Kd the derivative coefficient"
        + os.linesep
        + "   * @param source The PIDSource object that is used to get values"
        + os.linesep
        + "   * @param output The PIDOutput object that is set to the output value"
        + os.linesep
        + "   * @param period the loop time for doing calculations. This particularly"
        + os.linesep
        + "   *     effects calculations of the integral and differental terms. The default"
        + os.linesep
        + "   *     is 50ms."
        + os.linesep
        + "   */"
        + os.linesep
        + "  PIDController::PIDController(double Kp, double Ki, double Kd, PIDSource* source,"
        + os.linesep
        + "                               PIDOutput* output, double period)"
        + os.linesep,
    )
    test.add_output(
        "  /**"
        + os.linesep
        + "   * Allocate a PID object with the given constants for P, I, D."
        + os.linesep
        + "   *"
        + os.linesep
        + "   * More summary. Even more summary."
        + os.linesep
        + "   *"
        + os.linesep
        + "   * @param Kp The proportional coefficient."
        + os.linesep
        + "   * @param Ki The integral coefficient."
        + os.linesep
        + "   * @param Kd The derivative coefficient."
        + os.linesep
        + "   * @param source The PIDSource object that is used to get values."
        + os.linesep
        + "   * @param output The PIDOutput object that is set to the output value."
        + os.linesep
        + "   * @param period The loop time for doing calculations. This particularly effects"
        + os.linesep
        + "   *     calculations of the integral and differental terms. The default is 50ms."
        + os.linesep
        + "   */"
        + os.linesep
        + "  PIDController::PIDController(double Kp, double Ki, double Kd, PIDSource* source,"
        + os.linesep
        + "                               PIDOutput* output, double period)"
        + os.linesep,
        True,
    )

    test.run(OutputType.FILE)
