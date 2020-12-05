import os

from .tasktest import *
from wpiformat.virtualspecifier import VirtualSpecifier


def test_virtualspecifier():
    test = TaskTest(VirtualSpecifier())

    # Redundant virtual specifier on function
    test.add_input("./PWM.h",
        "class PWM : public SendableBase {" + os.linesep + \
        " public:" + os.linesep + \
        "  explicit PWM(int channel);" + os.linesep + \
        "  ~PWM() override;" + os.linesep + \
        os.linesep + \
        " protected:" + os.linesep + \
        "  virtual void InitSendable(SendableBuilder& builder) override;" + os.linesep + \
        "};" + os.linesep)
    test.add_output(
        "class PWM : public SendableBase {" + os.linesep + \
        " public:" + os.linesep + \
        "  explicit PWM(int channel);" + os.linesep + \
        "  ~PWM() override;" + os.linesep + \
        os.linesep + \
        " protected:" + os.linesep + \
        "  void InitSendable(SendableBuilder& builder) override;" + os.linesep + \
        "};" + os.linesep, True, True)

    # Redundant virtual specifier on const function
    test.add_input("./PIDController.h",
        "class PIDController : public PIDInterface {" + os.linesep + \
        " public:" + os.linesep + \
        "  virtual double GetP() const override;" + os.linesep + \
        "  virtual double GetI() const override;" + os.linesep + \
        "  virtual double GetD() const override;" + os.linesep + \
        "};" + os.linesep)
    test.add_output(
        "class PIDController : public PIDInterface {" + os.linesep + \
        " public:" + os.linesep + \
        "  double GetP() const override;" + os.linesep + \
        "  double GetI() const override;" + os.linesep + \
        "  double GetD() const override;" + os.linesep + \
        "};" + os.linesep, True, True)

    # Redundant final specifier on const function
    test.add_input("./PIDController.h",
        "class PIDController : public PIDInterface {" + os.linesep + \
        " public:" + os.linesep + \
        "  double GetP() const override;" + os.linesep + \
        "  double GetI() const final override;" + os.linesep + \
        "  double GetD() const override final;" + os.linesep + \
        "};" + os.linesep)
    test.add_output(
        "class PIDController : public PIDInterface {" + os.linesep + \
        " public:" + os.linesep + \
        "  double GetP() const override;" + os.linesep + \
        "  double GetI() const final;" + os.linesep + \
        "  double GetD() const final;" + os.linesep + \
        "};" + os.linesep, True, True)

    # Redundant virtual specifier on destructor
    test.add_input("./PWM.h",
        "class PWM : public SendableBase {" + os.linesep + \
        " public:" + os.linesep + \
        "  explicit PWM(int channel);" + os.linesep + \
        "  virtual ~PWM() override;" + os.linesep + \
        os.linesep + \
        "  virtual void SetRaw(uint16_t value);" + os.linesep + \
        "};" + os.linesep)
    test.add_output(
        "class PWM : public SendableBase {" + os.linesep + \
        " public:" + os.linesep + \
        "  explicit PWM(int channel);" + os.linesep + \
        "  ~PWM() override;" + os.linesep + \
        os.linesep + \
        "  virtual void SetRaw(uint16_t value);" + os.linesep + \
        "};" + os.linesep, True, True)

    # Idempotence with virtual specifier on destructor
    test.add_input("./PWM.h",
        "class PWM : public SendableBase {" + os.linesep + \
        " public:" + os.linesep + \
        "  explicit PWM(int channel);" + os.linesep + \
        "  virtual ~PWM();" + os.linesep + \
        "};" + os.linesep)
    test.add_output(
        "class PWM : public SendableBase {" + os.linesep + \
        " public:" + os.linesep + \
        "  explicit PWM(int channel);" + os.linesep + \
        "  virtual ~PWM();" + os.linesep + \
        "};" + os.linesep, False, True)

    test.run(OutputType.FILE)
