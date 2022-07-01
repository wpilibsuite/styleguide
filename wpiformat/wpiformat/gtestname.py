"""This task ensures GoogleTest test names follow the format
"TEST(ThingTest, Thing)".
"""

import regex

from wpiformat.task import Task


class GTestName(Task):
    @staticmethod
    def should_process_file(config_file, name):
        return config_file.is_cpp_file(name)

    def run_pipeline(self, config_file, name, lines):
        output = ""
        success = True

        test_name_rgx = regex.compile(
            r"\b(?P<test_type>TEST(_F|_P)?)\((?P<whitespace>\s*)(?P<test_suite>\w+), (?P<test_case>\w+)\)"
        )
        extract_location = 0
        for match in test_name_rgx.finditer(lines):
            test_type = match.group("test_type")
            test_suite = match.group("test_suite")
            test_case = match.group("test_case")

            # Write lines prior to test
            output += lines[extract_location : match.start()]

            # Write test type
            output += test_type + "("
            if match.group("whitespace"):
                output += match.group("whitespace")

            # Fix test suite name
            if test_suite.endswith("Tests"):
                test_suite = test_suite[:-1]
            if not test_suite.endswith("Test"):
                test_suite += "Test"

            # Write test suite name
            output += test_suite

            # Fix test case name
            if test_case == "Test" or test_case == "Tests":
                print(
                    f"Error: {name}: undescriptive test case name '{test_case}' in '{test_suite}.{test_case}'"
                )
                success = False
            else:
                if test_case.endswith("Test"):
                    test_case = test_case[:-4]
                if test_case.endswith("Tests"):
                    test_case = test_case[:-5]

            # Write test case name
            output += ", " + test_case + ")"

            extract_location = match.end()

        # If input has unprocessed lines, write them to output
        if extract_location < len(lines):
            output += lines[extract_location:]

        # Reset for next regex iteration
        lines = output
        output = ""

        inst_rgx = regex.compile(
            r"INSTANTIATE_TEST_SUITE_P\((?P<whitespace>\s*)(?P<test_suite>\w+), (?P<test_case>\w+)"
        )
        extract_location = 0
        for match in inst_rgx.finditer(lines):
            test_suite = match.group("test_suite")
            test_case = match.group("test_case")

            # Write lines prior to test
            output += lines[extract_location : match.start()]
            output += "INSTANTIATE_TEST_SUITE_P("
            if match.group("whitespace"):
                output += match.group("whitespace")

            # Fix test suite name
            if test_suite.endswith("Test"):
                test_suite += "s"
            if not test_suite.endswith("Tests"):
                test_suite += "Tests"

            # Write test suite name
            output += test_suite

            # Fix test case name
            if test_case.endswith("Tests"):
                test_case = test_case[:-1]
            if not test_case.endswith("Test"):
                test_case += "Test"

            # Write test case name
            output += ", " + test_case

            extract_location = match.end()

        # If input has unprocessed lines, write them to output
        if extract_location < len(lines):
            output += lines[extract_location:]

        return output, success
