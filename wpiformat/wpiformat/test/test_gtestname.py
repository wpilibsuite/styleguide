import os

from .test_tasktest import *
from wpiformat.gtestname import GTestName


def test_gtestname():
    test = TaskTest(GTestName())

    # Ignore TEST macro that isn't for GoogleTest
    test.add_input("./Test.cpp", "AXIS_TEST(Joystick, X)" + os.linesep)
    test.add_latest_input_as_output(True)

    for test_type in ["TEST", "TEST_F", "TEST_P"]:
        # Test suite replacements
        test.add_input("./Test.cpp", f"{test_type}(Foo, Bar) {{}}" + os.linesep)
        test.add_output(f"{test_type}(FooTest, Bar) {{}}" + os.linesep, True)
        test.add_input("./Test.cpp", f"{test_type}(FooTests, Bar) {{}}" + os.linesep)
        test.add_output(f"{test_type}(FooTest, Bar) {{}}" + os.linesep, True)

        # Test case replacements
        test.add_input("./Test.cpp", f"{test_type}(FooTest, BarTest) {{}}" + os.linesep)
        test.add_output(f"{test_type}(FooTest, Bar) {{}}" + os.linesep, True)

        # Test case only named "Test" or "Tests" should generate an error
        test.add_input("./Test.cpp", f"{test_type}(FooTest, Test) {{}}" + os.linesep)
        test.add_latest_input_as_output(False)
        test.add_input("./Test.cpp", f"{test_type}(FooTest, Tests) {{}}" + os.linesep)
        test.add_latest_input_as_output(False)

        # Idempotency
        test.add_input("./Test.cpp", f"{test_type}(FooTest, Bar) {{}}" + os.linesep)
        test.add_latest_input_as_output(True)

        # Duplicate test names to make sure file contents aren't dropped
        test.add_input(
            "./Test.cpp",
            f"{test_type}(FooTest, BarTest) {{}}"
            + os.linesep
            + os.linesep
            + f"{test_type}(FooTest, BarTest) {{}}"
            + os.linesep,
        )
        test.add_output(
            f"{test_type}(FooTest, Bar) {{}}"
            + os.linesep
            + os.linesep
            + f"{test_type}(FooTest, Bar) {{}}"
            + os.linesep,
            True,
        )

        # Test case replacement with args on next line
        test.add_input(
            "./Test.cpp",
            f"{test_type}(" + os.linesep + "    FooTest, BarTest) {{}}" + os.linesep,
        )
        test.add_output(
            f"{test_type}(" + os.linesep + "    FooTest, Bar) {{}}" + os.linesep, True
        )

    # INSTANTIATE_TEST_SUITE_P() test suite replacements
    test.add_input("./Test.cpp", "INSTANTIATE_TEST_SUITE_P(Foo, BarTest," + os.linesep)
    test.add_output("INSTANTIATE_TEST_SUITE_P(FooTests, BarTest," + os.linesep, True)
    test.add_input(
        "./Test.cpp", "INSTANTIATE_TEST_SUITE_P(FooTest, BarTest," + os.linesep
    )
    test.add_output("INSTANTIATE_TEST_SUITE_P(FooTests, BarTest," + os.linesep, True)

    # INSTANTIATE_TEST_SUITE_P() test case replacements
    test.add_input("./Test.cpp", "INSTANTIATE_TEST_SUITE_P(FooTests, Bar," + os.linesep)
    test.add_output("INSTANTIATE_TEST_SUITE_P(FooTests, BarTest," + os.linesep, True)
    test.add_input(
        "./Test.cpp", "INSTANTIATE_TEST_SUITE_P(FooTests, BarTests," + os.linesep
    )
    test.add_output("INSTANTIATE_TEST_SUITE_P(FooTests, BarTest," + os.linesep, True)

    # INSTANTIATE_TEST_SUITE_P() idempotency
    test.add_input(
        "./Test.cpp", "INSTANTIATE_TEST_SUITE_P(FooTests, BarTest," + os.linesep
    )
    test.add_latest_input_as_output(True)

    # INSTANTIATE_TEST_SUITE_P() test case replacement with args on next line
    test.add_input(
        "./Test.cpp",
        "INSTANTIATE_TEST_SUITE_P("
        + os.linesep
        + "    FooTests, BarTests,"
        + os.linesep,
    )
    test.add_output(
        "INSTANTIATE_TEST_SUITE_P("
        + os.linesep
        + "    FooTests, BarTest,"
        + os.linesep,
        True,
    )

    test.run(OutputType.FILE)
