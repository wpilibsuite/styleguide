"""This task runs cpplint.py on all C++ source files.

cpplint.py was converted from python 2 to python 3 with the following command
and a patch was applied:

2to3 -f all -f buffer -f idioms -f set_literal -f ws_comma -nw cpplint.py

diff --git a/styleguide/cpplint.py b/styleguide/cpplint.py
--- a/styleguide/cpplint.py
+++ b/styleguide/cpplint.py
@@ -5108,7 +5108,8 @@ def CheckCasts(filename, clean_lines, linenum, error):
 
   if not expecting_function:
     CheckCStyleCast(filename, clean_lines, linenum, 'static_cast',
-                    r'\((int|float|double|bool|char|u?int(16|32|64))\)', error)
+                    r'\(((unsigned )?(char|(short |long )?int|long)|float|'
+                    'double|bool|u?int(8_t|16_t|32_t|64_t))\)', error)
 
   # This doesn't catch all cases. Consider (const char * const)"hello".
   #
@@ -5120,7 +5121,7 @@ def CheckCasts(filename, clean_lines, linenum, error):
   else:
     # Check pointer casts for other than string constants
     CheckCStyleCast(filename, clean_lines, linenum, 'reinterpret_cast',
-                    r'\((\w+\s?\*+\s?)\)', error)
+                    r'\(((const )?\w+\s?\*+\s?)\)', error)
 
   # In addition, we look for people taking the address of a cast.  This
   # is dangerous -- casts can assign to temporaries, so the pointer doesn't
@@ -6003,7 +6004,6 @@ def ProcessFile(filename, vlevel, extra_check_functions=[]):
         Error(filename, linenum, 'whitespace/newline', 1,
               'Unexpected \\r (^M) found; better to use only \\n')
 
-  sys.stderr.write('Done processing %s\n' % filename)
   _RestoreFilters()
 
 
@@ -6102,17 +6102,9 @@ def ParseArguments(args):
 def main():
   filenames = ParseArguments(sys.argv[1:])
 
-  # Change stderr to write with replacement characters so we don't die
-  # if we try to print something containing non-ASCII characters.
-  sys.stderr = codecs.StreamReaderWriter(sys.stderr,
-                                         codecs.getreader('utf8'),
-                                         codecs.getwriter('utf8'),
-                                         'replace')
-
   _cpplint_state.ResetErrorCounts()
   for filename in filenames:
     ProcessFile(filename, _cpplint_state.verbose_level)
-  _cpplint_state.PrintErrorCounts()
 
   sys.exit(_cpplint_state.error_count > 0)
 
"""

"""cpplint.py was originally spawned as a subprocess whose output was filtered.
When it was moved into a separate repository, the difference in directories
required it to be used as a module. Redirecting stderr is not thread-safe and
overloading print() did not work, so the print statements causing that output
where removed from cpplint.py.
"""

import os
import sys

import cpplint
from task import Task

class Lint(Task):
    def getIncludeExtensions(self):
        return ["cpp", "h", "inc"]

    def run(self, name):
        # Handle running in either the root or styleguide directories
        cpplintPrefix = ""
        if os.getcwd().rpartition(os.sep)[2] != "styleguide":
            cpplintPrefix = "styleguide/"

        # Prepare arguments to cpplint.py
        savedArgv = sys.argv
        sys.argv = ["cpplint.py", "--filter="
                    "-build/c++11,"
                    "-build/header_guard,"
                    "-build/include,"
                    "-build/namespaces,"
                    "-readability/todo,"
                    "-runtime/references,"
                    "-runtime/string",
                    "--extensions=cpp,h,inc", name]

        # Run cpplint.py
        try:
            cpplint.main()
        except SystemExit:
            pass

        # Restore original arguments
        sys.argv = savedArgv
