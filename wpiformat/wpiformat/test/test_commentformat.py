import os

from .tasktest import *
from wpiformat.commentformat import CommentFormat


def test_commentformat():
    test = TaskTest(CommentFormat())

    # Empty comment
    test.add_input("./Test.h",
        "/**" + os.linesep + \
        " */" + os.linesep)
    test.add_latest_input_as_output(True)

    # Adds space before asterisks
    test.add_input("./Test.h",
        "/**" + os.linesep + \
        "*" + os.linesep + \
        "*/" + os.linesep)
    test.add_output(
        "/**" + os.linesep + \
        " */" + os.linesep, True, True)

    # Put /** on separate line
    test.add_input("./Test.h", "/** asdf */" + os.linesep)
    test.add_output(
        "/**" + os.linesep + \
        " * Asdf." + os.linesep + \
        " */" + os.linesep, True, True)

    # Paragraphs but no tags
    test.add_input("./Accelerometer.cpp",
        "/**" + os.linesep + \
        " * Get the x-axis acceleration" + os.linesep + \
        " *" + os.linesep + \
        " * This is a floating point value in units of 1 g-force" + os.linesep + \
        " */" + os.linesep)
    test.add_output(
        "/**" + os.linesep + \
        " * Get the x-axis acceleration." + os.linesep + \
        " *" + os.linesep + \
        " * This is a floating point value in units of 1 g-force." + os.linesep + \
        " */" + os.linesep, True, True)

    # Paragraphs but no tags
    test.add_input("./Accelerometer.cpp",
        "/**" + os.linesep + \
        " * Convert a 12-bit raw acceleration value into a scaled double in units of" + os.linesep + \
        " * 1 g-force, taking into account the accelerometer range." + os.linesep + \
        " */" + os.linesep)
    test.add_output(
        "/**" + os.linesep + \
        " * Convert a 12-bit raw acceleration value into a scaled double in units of 1" + os.linesep + \
        " * g-force, taking into account the accelerometer range." + os.linesep + \
        " */" + os.linesep, True, True)

    # @param tag but with blank line before it and no description
    test.add_input("./AnalogInput.cpp",
        "/**" + os.linesep + \
        " *" + os.linesep + \
        " * @param analogPortHandle Handle to the analog port." + os.linesep + \
        " */" + os.linesep)
    test.add_output(
        "/**" + os.linesep + \
        " * @param analogPortHandle Handle to the analog port." + os.linesep + \
        " */" + os.linesep, True, True)

    # Paragraph with @param and @return tags
    test.add_input("./AnalogAccumulator.cpp",
        "/**" + os.linesep + \
        " * Is the channel attached to an accumulator." + os.linesep + \
        " *" + os.linesep + \
        " * @param analogPortHandle Handle to the analog port." + os.linesep + \
        " * @return The analog channel is attached to an accumulator." + os.linesep + \
        " */" + os.linesep)
    test.add_latest_input_as_output(True)

    # Paragraph and @return with no empty line between them
    test.add_input("./AnalogTrigger.cpp",
        "/**" + os.linesep + \
        " * Return the InWindow output of the analog trigger." + os.linesep + \
        " *" + os.linesep + \
        " * True if the analog input is between the upper and lower limits." + os.linesep + \
        " * @return The InWindow output of the analog trigger." + os.linesep + \
        " */" + os.linesep)
    test.add_output(
        "/**" + os.linesep + \
        " * Return the InWindow output of the analog trigger." + os.linesep + \
        " *" + os.linesep + \
        " * True if the analog input is between the upper and lower limits." + os.linesep + \
        " *" + os.linesep + \
        " * @return The InWindow output of the analog trigger." + os.linesep + \
        " */" + os.linesep, True, True)

    # C++: paragraphs with @param tags
    test.add_input("./PIDController.cpp",
        "  /**" + os.linesep + \
        "   * Allocate a PID object with the given constants for P, I, D." + os.linesep + \
        "   *" + os.linesep + \
        "   * More summary." + os.linesep + \
        "   * Even more summary." + os.linesep + \
        "   *" + os.linesep + \
        "   * @param Kp the proportional coefficient" + os.linesep + \
        "   * @param Ki the integral coefficient" + os.linesep + \
        "   * @param Kd the derivative coefficient" + os.linesep + \
        "   * @param source The PIDSource object that is used to get values" + os.linesep + \
        "   * @param output The PIDOutput object that is set to the output value" + os.linesep + \
        "   * @param period the loop time for doing calculations. This particularly" + os.linesep + \
        "   *               effects calculations of the integral and differental terms." + os.linesep + \
        "   *               The default is 50ms." + os.linesep + \
        "   */" + os.linesep + \
        "  PIDController::PIDController(double Kp, double Ki, double Kd, PIDSource* source," + os.linesep + \
        "                               PIDOutput* output, double period)" + os.linesep)
    test.add_output(
        "  /**" + os.linesep + \
        "   * Allocate a PID object with the given constants for P, I, D." + os.linesep + \
        "   *" + os.linesep + \
        "   * More summary. Even more summary." + os.linesep + \
        "   *" + os.linesep + \
        "   * @param Kp     The proportional coefficient." + os.linesep + \
        "   * @param Ki     The integral coefficient." + os.linesep + \
        "   * @param Kd     The derivative coefficient." + os.linesep + \
        "   * @param source The PIDSource object that is used to get values." + os.linesep + \
        "   * @param output The PIDOutput object that is set to the output value." + os.linesep + \
        "   * @param period The loop time for doing calculations. This particularly" + os.linesep + \
        "   *               effects calculations of the integral and differental terms." + os.linesep + \
        "   *               The default is 50ms." + os.linesep + \
        "   */" + os.linesep + \
        "  PIDController::PIDController(double Kp, double Ki, double Kd, PIDSource* source," + os.linesep + \
        "                               PIDOutput* output, double period)" + os.linesep, True, True)

    # Java: paragraphs with @param tags idempotence
    test.add_input("./PIDController.java",
        "  /**" + os.linesep + \
        "   * Allocate a PID object with the given constants for P, I, D." + os.linesep + \
        "   *" + os.linesep + \
        "   * More summary." + os.linesep + \
        "   * Even more summary." + os.linesep + \
        "   *" + os.linesep + \
        "   * @param Kp the proportional coefficient" + os.linesep + \
        "   * @param Ki the integral coefficient" + os.linesep + \
        "   * @param Kd the derivative coefficient" + os.linesep + \
        "   * @param source The PIDSource object that is used to get values" + os.linesep + \
        "   * @param output The PIDOutput object that is set to the output value" + os.linesep + \
        "   * @param period the loop time for doing calculations. This particularly" + os.linesep + \
        "   *               effects calculations of the integral and differental terms." + os.linesep + \
        "   *               The default is 50ms." + os.linesep + \
        "   */" + os.linesep + \
        "  PIDController(double Kp, double Ki, double Kd, PIDSource source, PIDOutput output, double period)" + os.linesep)
    test.add_output(
        "  /**" + os.linesep + \
        "   * Allocate a PID object with the given constants for P, I, D." + os.linesep + \
        "   *" + os.linesep + \
        "   * <p>More summary. Even more summary." + os.linesep + \
        "   *" + os.linesep + \
        "   * @param Kp     The proportional coefficient." + os.linesep + \
        "   * @param Ki     The integral coefficient." + os.linesep + \
        "   * @param Kd     The derivative coefficient." + os.linesep + \
        "   * @param source The PIDSource object that is used to get values." + os.linesep + \
        "   * @param output The PIDOutput object that is set to the output value." + os.linesep + \
        "   * @param period The loop time for doing calculations. This particularly effects calculations of" + os.linesep + \
        "   *               the integral and differental terms. The default is 50ms." + os.linesep + \
        "   */" + os.linesep + \
        "  PIDController(double Kp, double Ki, double Kd, PIDSource source, PIDOutput output, double period)" + os.linesep, True, True)

    test.add_input("./PIDController.java",
        "  /**" + os.linesep + \
        "   * Allocate a PID object with the given constants for P, I, D." + os.linesep + \
        "   *" + os.linesep + \
        "   * <p>More summary. Even more summary." + os.linesep + \
        "   *" + os.linesep + \
        "   * @param Kp     The proportional coefficient." + os.linesep + \
        "   * @param Ki     The integral coefficient." + os.linesep + \
        "   * @param Kd     The derivative coefficient." + os.linesep + \
        "   * @param source The PIDSource object that is used to get values." + os.linesep + \
        "   * @param output The PIDOutput object that is set to the output value." + os.linesep + \
        "   * @param period The loop time for doing calculations. This particularly effects calculations of" + os.linesep + \
        "   *               the integral and differental terms. The default is 50ms." + os.linesep + \
        "   */" + os.linesep + \
        "  PIDController(double Kp, double Ki, double Kd, PIDSource source, PIDOutput output, double period)" + os.linesep)
    test.add_latest_input_as_output(True)

    # Java: Don't count "{@" as tag (only "@" at beginning of line)
    test.add_input("./Test.java",
        "/**" + os.linesep + \
        " * This is a {@link test} description." + os.linesep + \
        " *" + os.linesep + \
        " * @param test Test parameter." + os.linesep + \
        " */" + os.linesep)
    test.add_latest_input_as_output(True)

    # Java: Make sure {@link ...} is wrapped atomically
    test.add_input("./Test.java",
        "/**" + os.linesep + \
        " * This is a sentence. This is a really, really, really, really long sentence with a Javadoc {@link test} in it." + os.linesep + \
        " *" + os.linesep + \
        " * @param test Test parameter." + os.linesep + \
        " */" + os.linesep)
    test.add_output(
        "/**" + os.linesep + \
        " * This is a sentence. This is a really, really, really, really long sentence with a Javadoc" + os.linesep + \
        " * {@link test} in it." + os.linesep + \
        " *" + os.linesep + \
        " * @param test Test parameter." + os.linesep + \
        " */" + os.linesep, True, True)

    # List ("-" bullets)
    test.add_input("./DigitalInternal.h",
        "/**" + os.linesep + \
        " * The default PWM period is in ms." + os.linesep + \
        " *" + os.linesep + \
        " * - 20ms periods (50 Hz) are the \"safest\" setting in that this works for all" + os.linesep + \
        " *   devices" + os.linesep + \
        " * - 20ms periods seem to be desirable for Vex Motors" + os.linesep + \
        " * - 20ms periods are the specified period for HS-322HD servos, but work" + os.linesep + \
        " *   reliably down to 10.0 ms; starting at about 8.5ms, the servo sometimes hums" + os.linesep + \
        " *   and get hot; by 5.0ms the hum is nearly continuous" + os.linesep + \
        " * - 10ms periods work well for Victor 884" + os.linesep + \
        " * - 5ms periods allows higher update rates for Luminary Micro Jaguar speed" + os.linesep + \
        " *   controllers. Due to the shipping firmware on the Jaguar, we can't run the" + os.linesep + \
        " *   update period less than 5.05 ms." + os.linesep + \
        " *" + os.linesep + \
        " * kDefaultPwmPeriod is the 1x period (5.05 ms). In hardware, the period" + os.linesep + \
        " * scaling is implemented as an output squelch to get longer periods for old" + os.linesep + \
        " * devices." + os.linesep + \
        " */" + os.linesep)
    test.add_latest_input_as_output(True)

    # List ("+" bullets)
    test.add_input("./DigitalInternal.h",
        "/**" + os.linesep + \
        " * The default PWM period is in ms." + os.linesep + \
        " *" + os.linesep + \
        " * + 20ms periods (50 Hz) are the \"safest\" setting in that this works for all" + os.linesep + \
        " *   devices" + os.linesep + \
        " * + 20ms periods seem to be desirable for Vex Motors" + os.linesep + \
        " * + 20ms periods are the specified period for HS-322HD servos, but work" + os.linesep + \
        " *   reliably down to 10.0 ms; starting at about 8.5ms, the servo sometimes hums" + os.linesep + \
        " *   and get hot; by 5.0ms the hum is nearly continuous" + os.linesep + \
        " * + 10ms periods work well for Victor 884" + os.linesep + \
        " * + 5ms periods allows higher update rates for Luminary Micro Jaguar speed" + os.linesep + \
        " *   controllers. Due to the shipping firmware on the Jaguar, we can't run the" + os.linesep + \
        " *   update period less than 5.05 ms." + os.linesep + \
        " *" + os.linesep + \
        " * kDefaultPwmPeriod is the 1x period (5.05 ms). In hardware, the period" + os.linesep + \
        " * scaling is implemented as an output squelch to get longer periods for old" + os.linesep + \
        " * devices." + os.linesep + \
        " */" + os.linesep)
    test.add_latest_input_as_output(True)

    # List ("*" bullets)
    test.add_input("./DigitalInternal.h",
        "/**" + os.linesep + \
        " * The default PWM period is in ms." + os.linesep + \
        " *" + os.linesep + \
        " * * 20ms periods (50 Hz) are the \"safest\" setting in that this works for all" + os.linesep + \
        " *   devices" + os.linesep + \
        " * * 20ms periods seem to be desirable for Vex Motors" + os.linesep + \
        " * * 20ms periods are the specified period for HS-322HD servos, but work" + os.linesep + \
        " *   reliably down to 10.0 ms; starting at about 8.5ms, the servo sometimes hums" + os.linesep + \
        " *   and get hot; by 5.0ms the hum is nearly continuous" + os.linesep + \
        " * * 10ms periods work well for Victor 884" + os.linesep + \
        " * * 5ms periods allows higher update rates for Luminary Micro Jaguar speed" + os.linesep + \
        " *   controllers. Due to the shipping firmware on the Jaguar, we can't run the" + os.linesep + \
        " *   update period less than 5.05 ms." + os.linesep + \
        " *" + os.linesep + \
        " * kDefaultPwmPeriod is the 1x period (5.05 ms). In hardware, the period" + os.linesep + \
        " * scaling is implemented as an output squelch to get longer periods for old" + os.linesep + \
        " * devices." + os.linesep + \
        " */" + os.linesep)
    test.add_latest_input_as_output(True)

    # List (numbered items)
    test.add_input("./DigitalInternal.h",
        "/**" + os.linesep + \
        " * The default PWM period is in ms." + os.linesep + \
        " *" + os.linesep + \
        " * 1. 20ms periods (50 Hz) are the \"safest\" setting in that this works for all" + os.linesep + \
        " *    devices" + os.linesep + \
        " * 2. 20ms periods seem to be desirable for Vex Motors" + os.linesep + \
        " * 3. 20ms periods are the specified period for HS-322HD servos, but work" + os.linesep + \
        " *    reliably down to 10.0 ms; starting at about 8.5ms, the servo sometimes hums" + os.linesep + \
        " *    and get hot; by 5.0ms the hum is nearly continuous" + os.linesep + \
        " * 4. 10ms periods work well for Victor 884" + os.linesep + \
        " * 5. 5ms periods allows higher update rates for Luminary Micro Jaguar speed" + os.linesep + \
        " *    controllers. Due to the shipping firmware on the Jaguar, we can't run the" + os.linesep + \
        " *    update period less than 5.05 ms." + os.linesep + \
        " *" + os.linesep + \
        " * kDefaultPwmPeriod is the 1x period (5.05 ms). In hardware, the period" + os.linesep + \
        " * scaling is implemented as an output squelch to get longer periods for old" + os.linesep + \
        " * devices." + os.linesep + \
        " */" + os.linesep)
    test.add_latest_input_as_output(True)

    test.run(OutputType.FILE)
