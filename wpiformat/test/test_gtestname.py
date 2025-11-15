from wpiformat.gtestname import GTestName

from .test_tasktest import *


def test_gtestname():
    # Ignore TEST macro that isn't for GoogleTest
    contents = "AXIS_TEST(Joystick, X)\n"
    run_and_check_file(GTestName(), "./Test.cpp", contents, contents, True)

    for test_type in ["TEST", "TEST_F", "TEST_P"]:
        # Test suite replacements
        run_and_check_file(
            GTestName(),
            "./Test.cpp",
            f"{test_type}(Foo, Bar) {{}}\n",
            f"{test_type}(FooTest, Bar) {{}}\n",
            True,
        )
        run_and_check_file(
            GTestName(),
            "./Test.cpp",
            f"{test_type}(FooTests, Bar) {{}}\n",
            f"{test_type}(FooTest, Bar) {{}}\n",
            True,
        )

        # Test case replacements
        run_and_check_file(
            GTestName(),
            "./Test.cpp",
            f"{test_type}(FooTest, BarTest) {{}}\n",
            f"{test_type}(FooTest, Bar) {{}}\n",
            True,
        )

        # Test case only named "Test" or "Tests" should generate an error
        contents = f"{test_type}(FooTest, Test) {{}}\n"
        run_and_check_file(GTestName(), "./Test.cpp", contents, contents, False)
        contents = f"{test_type}(FooTest, Tests) {{}}\n"
        run_and_check_file(GTestName(), "./Test.cpp", contents, contents, False)

        # Idempotency
        contents = f"{test_type}(FooTest, Bar) {{}}\n"
        run_and_check_file(GTestName(), "./Test.cpp", contents, contents, True)

        # Duplicate test names to make sure file contents aren't dropped
        run_and_check_file(
            GTestName(),
            "./Test.cpp",
            f"""{test_type}(FooTest, BarTest) {{}}

{test_type}(FooTest, BarTest) {{}}
""",
            f"""{test_type}(FooTest, Bar) {{}}

{test_type}(FooTest, Bar) {{}}
""",
            True,
        )

        # Test case replacement with args on next line
        run_and_check_file(
            GTestName(),
            "./Test.cpp",
            f"""{test_type}(
    FooTest, BarTest) {{}}
""",
            f"""{test_type}(
    FooTest, Bar) {{}}
""",
            True,
        )

    # INSTANTIATE_TEST_SUITE_P() test suite replacements
    run_and_check_file(
        GTestName(),
        "./Test.cpp",
        "INSTANTIATE_TEST_SUITE_P(Foo, BarTest,\n",
        "INSTANTIATE_TEST_SUITE_P(FooTests, BarTest,\n",
        True,
    )
    run_and_check_file(
        GTestName(),
        "./Test.cpp",
        "INSTANTIATE_TEST_SUITE_P(FooTest, BarTest,\n",
        "INSTANTIATE_TEST_SUITE_P(FooTests, BarTest,\n",
        True,
    )

    # INSTANTIATE_TEST_SUITE_P() test case replacements
    run_and_check_file(
        GTestName(),
        "./Test.cpp",
        "INSTANTIATE_TEST_SUITE_P(FooTests, Bar,\n",
        "INSTANTIATE_TEST_SUITE_P(FooTests, BarTest,\n",
        True,
    )
    run_and_check_file(
        GTestName(),
        "./Test.cpp",
        "INSTANTIATE_TEST_SUITE_P(FooTests, BarTests,\n",
        "INSTANTIATE_TEST_SUITE_P(FooTests, BarTest,\n",
        True,
    )

    # INSTANTIATE_TEST_SUITE_P() idempotency
    contents = "INSTANTIATE_TEST_SUITE_P(FooTests, BarTest,\n"
    run_and_check_file(GTestName(), "./Test.cpp", contents, contents, True)

    # INSTANTIATE_TEST_SUITE_P() test case replacement with args on next line
    run_and_check_file(
        GTestName(),
        "./Test.cpp",
        """INSTANTIATE_TEST_SUITE_P(
    FooTests, BarTests,
""",
        """INSTANTIATE_TEST_SUITE_P(
    FooTests, BarTest,
""",
        True,
    )
