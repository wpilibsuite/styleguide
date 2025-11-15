"""This task formats JNI signatures according to javah's output.

The format is of the form:

JNIEXPORT <return type> JNICALL
Java_blah
  (args, more args)
{
  // code here

If string of arguments exceeds 80 characters in length, it wraps as follows:

  (args,
   more args)
{
  // code here

The preceding comment containing the Class, Method, and Signature is also
automatically generated based on the function's return type and arguments.
"""

import re

from wpiformat.config import Config
from wpiformat.task import PipelineTask


class Jni(PipelineTask):
    @staticmethod
    def should_process_file(config_file: Config, filename: str) -> bool:
        return config_file.is_cpp_src_file(filename)

    @staticmethod
    def map_jni_type(type_name: str) -> str:
        ret = ""
        if type_name.endswith("*") or type_name.endswith("Array"):
            ret += "["

        if type_name.startswith("jboolean"):
            return ret + "Z"
        elif type_name.startswith("jbyte"):
            return ret + "B"
        elif type_name.startswith("jchar"):
            return ret + "C"
        elif type_name.startswith("jshort"):
            return ret + "S"
        elif type_name.startswith("jint"):
            return ret + "I"
        elif type_name.startswith("jlong"):
            return ret + "J"
        elif type_name.startswith("jfloat"):
            return ret + "F"
        elif type_name.startswith("jdouble"):
            return ret + "D"
        elif type_name.startswith("void"):
            return ret + "V"
        elif type_name.startswith("jstring"):
            return ret + "Ljava/lang/String;"
        elif type_name.startswith("jobject"):
            return ret + "Ljava/lang/Object;"
        else:
            return ret + "?"

    def run_pipeline(
        self, config_file: Config, filename: str, lines: str
    ) -> tuple[str, bool]:
        linesep = super().get_linesep(lines)

        regex_str_sig = (
            r"(/\*(.|\n)*?\*/\s+)?"
            + r"JNIEXPORT\s+(?P<ret>\w+)\s+JNICALL\s+"
            + r"(?P<func>Java_\w+)\s*\(\s*"
            + r"(?P<env_type>JNIEnv\s*\*\s*)"
            + r"(?P<env_name>\w+)?,\s*"
            + r"(?P<param_type>jclass|jobject)\s*(?P<param_name>\w*)?"
        )
        regex_sig = re.compile(regex_str_sig)

        regex_str_func = r"Java_(?P<class>\w+)_(?P<method>[^_]+)$"
        regex_func = re.compile(regex_str_func)

        # Matches a comma followed by the type, an optional variable name, and
        # an optional closing parenthesis
        regex_str_arg = (
            r", \s* (?P<arg>(?P<arg_type>[\w\*]+)(\s+ \w+)?)|\)\s*" r"(?P<trailing>{|;)"
        )
        regex_arg = re.compile(regex_str_arg, re.VERBOSE)

        output = ""
        pos = 0
        for match_sig in regex_sig.finditer(lines):
            comment = ""
            signature = ""

            if match_sig.start() > 0:
                output += lines[pos : match_sig.start()]

            # Add JNI-specific args
            jni_args = "  ("
            if match_sig.group("env_type"):
                jni_args += match_sig.group("env_type")
            if match_sig.group("env_name"):
                jni_args += match_sig.group("env_name")
            jni_args += ", " + match_sig.group("param_type")
            if match_sig.group("param_name"):
                jni_args += " " + match_sig.group("param_name")

            # Write JNI function comment. Splitting at "__" removes overload
            # annotation from method comment
            match = regex_func.search(match_sig.group("func").split("__")[0])
            if not match:
                return lines, False
            comment += f"""/*
 * Class:     {match.group("class")}
 * Method:    {match.group("method")}
 * Signature: (""".replace(
                "\n", linesep
            )

            signature += f"""JNIEXPORT {match_sig.group("ret")} JNICALL
{match_sig.group("func")}
{jni_args}""".replace(
                "\n", linesep
            )

            # Add other args
            line_length = len(jni_args)
            for match_arg in regex_arg.finditer(lines[match_sig.end() :]):
                if ")" in match_arg.group():
                    break
                # If args going past 80 characters
                elif (
                    line_length + len(", ") + len(match_arg.group("arg")) + len(")")
                    > 80
                ):
                    # Put current arg on next line and set line_length to
                    # reflect that
                    signature += "," + linesep + "   " + match_arg.group("arg")
                    line_length = len("   " + match_arg.group("arg"))
                else:
                    signature += ", " + match_arg.group("arg")
                    line_length += len(", ") + len(match_arg.group("arg"))
                comment += self.map_jni_type(match_arg.group("arg_type"))
            comment += f"""){self.map_jni_type(match_sig.group("ret"))}
 */
""".replace(
                "\n", linesep
            )

            # Output correct trailing character for declaration vs definition
            if match_arg.group("trailing") == "{":
                signature += f"){linesep}{{"
            else:
                signature += ");"

            output += comment + signature

            pos = match_sig.end() + match_arg.end()

        # Write rest of file
        if pos < len(lines):
            output += lines[pos:]

        if output == "":
            return lines, True
        else:
            return output, True
