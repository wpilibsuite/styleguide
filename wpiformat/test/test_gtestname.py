from wpiformat.gtestname import GTestName

from .test_tasktest import *


def test_gtestname():
    test = TaskTest(GTestName())

    # Ignore TEST macro that isn't for GoogleTest
    test.add_input("./Test.cpp", "AXIS_TEST(Joystick, X)\n")
    test.add_latest_input_as_output(True)

    for test_type in ["TEST", "TEST_F", "TEST_P"]:
        # Test suite replacements
        test.add_input("./Test.cpp", f"{test_type}(Foo, Bar) {{}}\n")
        test.add_output(f"{test_type}(FooTest, Bar) {{}}\n", True)
        test.add_input("./Test.cpp", f"{test_type}(FooTests, Bar) {{}}\n")
        test.add_output(f"{test_type}(FooTest, Bar) {{}}\n", True)

        # Test case replacements
        test.add_input("./Test.cpp", f"{test_type}(FooTest, BarTest) {{}}\n")
        test.add_output(f"{test_type}(FooTest, Bar) {{}}\n", True)

        # Test case only named "Test" or "Tests" should generate an error
        test.add_input("./Test.cpp", f"{test_type}(FooTest, Test) {{}}\n")
        test.add_latest_input_as_output(False)
        test.add_input("./Test.cpp", f"{test_type}(FooTest, Tests) {{}}\n")
        test.add_latest_input_as_output(False)

        # Idempotency
        test.add_input("./Test.cpp", f"{test_type}(FooTest, Bar) {{}}\n")
        test.add_latest_input_as_output(True)

        # Duplicate test names to make sure file contents aren't dropped
        test.add_input(
            "./Test.cpp",
            f"""{test_type}(FooTest, BarTest) {{}}

{test_type}(FooTest, BarTest) {{}}
""",
        )
        test.add_output(
            f"""{test_type}(FooTest, Bar) {{}}

{test_type}(FooTest, Bar) {{}}
""",
            True,
        )

        # Test case replacement with args on next line
        test.add_input(
            "./Test.cpp",
            f"""{test_type}(
    FooTest, BarTest) {{}}
""",
        )
        test.add_output(
            f"""{test_type}(
    FooTest, Bar) {{}}
""",
            True,
        )

    # INSTANTIATE_TEST_SUITE_P() test suite replacements
    test.add_input("./Test.cpp", "INSTANTIATE_TEST_SUITE_P(Foo, BarTest,\n")
    test.add_output("INSTANTIATE_TEST_SUITE_P(FooTests, BarTest,\n", True)
    test.add_input("./Test.cpp", "INSTANTIATE_TEST_SUITE_P(FooTest, BarTest,\n")
    test.add_output("INSTANTIATE_TEST_SUITE_P(FooTests, BarTest,\n", True)

    # INSTANTIATE_TEST_SUITE_P() test case replacements
    test.add_input("./Test.cpp", "INSTANTIATE_TEST_SUITE_P(FooTests, Bar,\n")
    test.add_output("INSTANTIATE_TEST_SUITE_P(FooTests, BarTest,\n", True)
    test.add_input("./Test.cpp", "INSTANTIATE_TEST_SUITE_P(FooTests, BarTests,\n")
    test.add_output("INSTANTIATE_TEST_SUITE_P(FooTests, BarTest,\n", True)

    # INSTANTIATE_TEST_SUITE_P() idempotency
    test.add_input("./Test.cpp", "INSTANTIATE_TEST_SUITE_P(FooTests, BarTest,\n")
    test.add_latest_input_as_output(True)

    # INSTANTIATE_TEST_SUITE_P() test case replacement with args on next line
    test.add_input(
        "./Test.cpp",
        """INSTANTIATE_TEST_SUITE_P(
    FooTests, BarTests,
""",
    )
    test.add_output(
        """INSTANTIATE_TEST_SUITE_P(
    FooTests, BarTest,
""",
        True,
    )

    test.run(OutputType.FILE)
