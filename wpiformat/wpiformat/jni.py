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

import regex

from wpiformat.task import Task


class Jni(Task):

    def should_process_file(self, config_file, name):
        return config_file.is_cpp_src_file(name)

    def map_jni_type(self, type_name):
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

    def run_pipeline(self, config_file, name, lines):
        linesep = Task.get_linesep(lines)

        regex_str_sig = "(/\*(?>(.|\n)*?\*/)\s+)?" + \
            "JNIEXPORT\s+(?P<ret>\w+)\s+JNICALL\s+" + \
            "(?P<func>Java_\w+)\s*\(\s*" + \
            "(?P<env_type>JNIEnv\s*\*\s*)" + \
            "(?P<env_name>\w+)?,\s*jclass\s*(?P<jclass_name>\w*)?"
        regex_sig = regex.compile(regex_str_sig)

        regex_str_func = "Java_(?P<class>\w+)_(?P<method>[^_]+)$"
        regex_func = regex.compile(regex_str_func)

        # Matches a comma followed by the type, an optional variable name, and
        # an optional closing parenthesis
        regex_str_arg = (", \s* (?P<arg>(?P<arg_type>[\w\*]+)(\s+ \w+)?)|\)\s*"
                         "(?P<trailing>{|;)")
        regex_arg = regex.compile(regex_str_arg, regex.VERBOSE)

        output = ""
        pos = 0
        for match_sig in regex_sig.finditer(lines):
            comment = ""
            signature = ""

            if match_sig.start() > 0:
                output += lines[pos:match_sig.start()]

            # Add JNI-specific args
            jni_args = "  ("
            if match_sig.group("env_type"):
                jni_args += match_sig.group("env_type")
            if match_sig.group("env_name"):
                jni_args += match_sig.group("env_name")
            jni_args += ", jclass"
            if match_sig.group("jclass_name"):
                jni_args += " " + match_sig.group("jclass_name")

            # Write JNI function comment. Splitting at "__" removes overload
            # annotation from method comment
            match = regex_func.search(match_sig.group("func").split("__")[0])
            comment += "/*" + linesep + \
                " * Class:     " + match.group("class") + linesep + \
                " * Method:    " + match.group("method") + linesep + \
                " * Signature: ("

            signature += "JNIEXPORT " + match_sig.group("ret") + " JNICALL" + \
                linesep + match_sig.group("func") + linesep + jni_args

            # Add other args
            line_length = len(jni_args)
            for match_arg in regex_arg.finditer(lines[match_sig.end():]):
                if ")" in match_arg.group():
                    break
                # If args going past 80 characters
                elif line_length + len(", ") + len(
                        match_arg.group("arg")) + len(")") > 80:
                    # Put current arg on next line and set line_length to
                    # reflect that
                    signature += "," + linesep + "   " + match_arg.group("arg")
                    line_length = len("   " + match_arg.group("arg"))
                else:
                    signature += ", " + match_arg.group("arg")
                    line_length += len(", ") + len(match_arg.group("arg"))
                comment += self.map_jni_type(match_arg.group("arg_type"))
            comment += ")" + self.map_jni_type(match_sig.group("ret")) + linesep + \
                " */" + linesep

            # Output correct trailing character for declaration vs definition
            if match_arg.group("trailing") == "{":
                signature += ")" + linesep + "{"
            else:
                signature += ");"

            output += comment + signature

            pos = match_sig.end() + match_arg.end()

        # Write rest of file
        if pos < len(lines):
            output += lines[pos:]

        if output == "" or output == lines:
            return (lines, False, True)
        else:
            return (output, True, True)
