#!/usr/bin/env python
#
# Copyright (c) 2009 Google Inc. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#    * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Does google-lint on c++ files.

The goal of this script is to identify places in the code that *may*
be in non-compliance with google style.  It does not attempt to fix
up these problems -- the point is to educate.  It does also not
attempt to find all problems, or to ensure that everything it does
find is legitimately a problem.

In particular, we can get very confused by /* and // inside strings!
We do a small hack, which is to ignore //'s with "'s after them on the
same line, but it is far from perfect (in either direction).
"""

import codecs
import copy
import getopt
import glob
import itertools
import math  # for log
import os
import regex
import string
import sys

try:
    import re._compiler as sre_compile
except ImportError:  # Python < 3.11
    import sre_compile

# if empty, use defaults
_header_regex = regex.compile("a^")

# if empty, use defaults
_source_regex = regex.compile("a^")


# Files which match the regex are considered to be header
# files (and will undergo different style checks).
# This set can be extended by using the --headers
# option
def IsHeaderFile(filename):
  return _header_regex.search(filename)

def IsSourceFile(filename):
  return _source_regex.search(filename)


_USAGE = r"""
Syntax: cpplint.py [--repository=path]
                   [--headers=header_regex]
                   [--srcs=src_regex]
        <file> [file] ...

  The style guidelines this tries to follow are those in
    https://google.github.io/styleguide/cppguide.html

  Every problem is given a confidence score from 1-5, with 5 meaning we are
  certain of the problem, and 1 meaning it could be a legitimate construct.
  This will miss some errors, and is not a substitute for a code review.

  To suppress false-positive errors of a certain category, add a
  'NOLINT(category)' comment to the line.  NOLINT or NOLINT(*)
  suppresses errors of all categories on that line.

  The files passed in will be linted; at least one file must be provided.

  Flags:

    repository=path
      The top level directory of the repository, used to derive the header
      guard CPP variable. By default, this is determined by searching for a
      path that contains .git, .hg, or .svn. When this flag is specified, the
      given path is used instead. This option allows the header guard CPP
      variable to remain consistent even if members of a team have different
      repository root directories (such as when checking out a subdirectory
      with SVN). In addition, users of non-mainstream version control systems
      can use this flag to ensure readable header guard CPP variables.

      Examples:
        Assuming that Alice checks out ProjectName and Bob checks out
        ProjectName/trunk and trunk contains src/chrome/ui/browser.h, then
        with no --repository flag, the header guard CPP variable will be:

        Alice => TRUNK_SRC_CHROME_BROWSER_UI_BROWSER_H_
        Bob   => SRC_CHROME_BROWSER_UI_BROWSER_H_

        If Alice uses the --repository=trunk flag and Bob omits the flag or
        uses --repository=. then the header guard CPP variable will be:

        Alice => SRC_CHROME_BROWSER_UI_BROWSER_H_
        Bob   => SRC_CHROME_BROWSER_UI_BROWSER_H_

    srcs=src_regex
      The regex for source files that cpplint will check

      Examples:
        --srcs=\.c$|\.cpp$

    headers=header_regex
      The regex for header files that cpplint will use

      Examples:
        --headers=\.h$|\.hpp$|\.inc$
"""

# We categorize each error message we print.  Here are the categories.
# We want an explicit list so we can list them all in cpplint --filter=.
# If you add a new error message with a new category, add it to the list
# here!  cpplint_unittest.py should tell you if you forget to do this.
_ERROR_CATEGORIES = [
    'build/class',
    'build/deprecated',
    'build/endif_comment',
    'build/explicit_make_pair',
    'build/header_guard',
    'build/include_order',
    'build/include_what_you_use',
    'build/printf_format',
    'build/storage_class',
    'readability/alt_tokens',
    'readability/braces',
    'readability/casting',
    'readability/check',
    'readability/constructors',
    'readability/fn_size',
    'readability/inheritance',
    'readability/multiline_comment',
    'readability/multiline_string',
    'readability/namespace',
    'readability/nolint',
    'readability/nul',
    'readability/strings',
    'readability/utf8',
    'runtime/arrays',
    'runtime/casting',
    'runtime/explicit',
    'runtime/int',
    'runtime/init',
    'runtime/invalid_increment',
    'runtime/member_string_references',
    'runtime/memset',
    'runtime/operator',
    'runtime/printf',
    'runtime/printf_format',
    'whitespace/blank_line',
    'whitespace/comments',
    'whitespace/empty_conditional_body',
    'whitespace/empty_if_body',
    'whitespace/empty_loop_body',
    'whitespace/forcolon',
    'whitespace/newline',
    'whitespace/operators',
    'whitespace/parens',
    'whitespace/semicolon',
    'whitespace/todo',
    ]

# The default list of categories suppressed for C (not C++) files.
_DEFAULT_C_SUPPRESSED_CATEGORIES = [
    'readability/casting',
    ]

# We used to check for high-bit characters, but after much discussion we
# decided those were OK, as long as they were in UTF-8 and didn't represent
# hard-coded international strings, which belong in a separate i18n file.

# Type names
_TYPES = regex.compile(
    r'^(?:'
    # [dcl.type.simple]
    r'(char(16_t|32_t)?)|wchar_t|'
    r'bool|short|int|long|signed|unsigned|float|double|'
    # [support.types]
    r'(ptrdiff_t|size_t|max_align_t|nullptr_t)|'
    # [cstdint.syn]
    r'(u?int(_fast|_least)?(8|16|32|64)_t)|'
    r'(u?int(max|ptr)_t)|'
    r')$')


# These headers are excluded from [build/include] checks:
# - Anything not following google file name conventions (containing an
#   uppercase character, such as Python.h or nsStringAPI.h, for example).
# - Lua headers.
_THIRD_PARTY_HEADERS_PATTERN = regex.compile(
    r'^(?:[^/]*[A-Z][^/]*\.h|lua\.h|lauxlib\.h|lualib\.h)$')

# Pattern that matches only complete whitespace, possibly across multiple lines.
_EMPTY_CONDITIONAL_BODY_PATTERN = regex.compile(r'^\s*$', regex.DOTALL)

# Alternative tokens and their replacements.  For full list, see section 2.5
# Alternative tokens [lex.digraph] in the C++ standard.
#
# Digraphs (such as '%:') are not included here since it's a mess to
# match those on a word boundary.
_ALT_TOKEN_REPLACEMENT = {
    'and': '&&',
    'bitor': '|',
    'or': '||',
    'xor': '^',
    'compl': '~',
    'bitand': '&',
    'and_eq': '&=',
    'or_eq': '|=',
    'xor_eq': '^=',
    'not': '!',
    'not_eq': '!='
    }

# Compile regular expression that matches all the above keywords.  The "[ =()]"
# bit is meant to avoid matching these keywords outside of boolean expressions.
#
# False positives include C-style multi-line comments and multi-line strings
# but those have always been troublesome for cpplint.
_ALT_TOKEN_REPLACEMENT_PATTERN = regex.compile(
    r'[ =()](' + ('|'.join(_ALT_TOKEN_REPLACEMENT.keys())) + r')(?=[ (]|$)')


# These constants define the current inline assembly state
_NO_ASM = 0       # Outside of inline assembly block
_INSIDE_ASM = 1   # Inside inline assembly block
_END_ASM = 2      # Last line of inline assembly block
_BLOCK_ASM = 3    # The whole block is an inline assembly block

# Match start of assembly blocks
_MATCH_ASM = regex.compile(r'^\s*(?:asm|_asm|__asm|__asm__)'
                        r'(?:\s+(volatile|__volatile__))?'
                        r'\s*[{(]')

# Match strings that indicate we're working on a C (not C++) file.
_SEARCH_C_FILE = regex.compile(r'\b(?:LINT_C_FILE|'
                            r'vim?:\s*.*(\s*|:)filetype=c(\s*|:|$))')

_regexp_compile_cache = {}

# {str, set(int)}: a map from error categories to sets of linenumbers
# on which those errors are expected and should be suppressed.
_error_suppressions = {}

if sys.version_info < (3,):
  #  -- pylint: disable=no-member
  # BINARY_TYPE = str
  itervalues = dict.itervalues
  iteritems = dict.iteritems
else:
  # BINARY_TYPE = bytes
  itervalues = dict.values
  iteritems = dict.items


def unicode_escape_decode(x):
  if sys.version_info < (3,):
    return codecs.unicode_escape_decode(x)[0]
  else:
    return x

# {str, bool}: a map from error categories to booleans which indicate if the
# category should be suppressed for every line.
_global_error_suppressions = {}


def ParseNolintSuppressions(filename, raw_line, linenum, error):
  """Updates the global list of line error-suppressions.

  Parses any NOLINT comments on the current line, updating the global
  error_suppressions store.  Reports an error if the NOLINT comment
  was malformed.

  Args:
    filename: str, the name of the input file.
    raw_line: str, the line of input text, with comments.
    linenum: int, the number of the current line.
    error: function, an error handler.
  """
  matched = Search(r'\bNOLINT(NEXTLINE)?\b(\([^)]+\))?', raw_line)
  if matched:
    if matched.group(1):
      suppressed_line = linenum + 1
    else:
      suppressed_line = linenum
    category = matched.group(2)
    if category in (None, '(*)'):  # => "suppress all"
      _error_suppressions.setdefault(None, set()).add(suppressed_line)
    else:
      if category.startswith('(') and category.endswith(')'):
        category = category[1:-1]
        if category in _ERROR_CATEGORIES:
          _error_suppressions.setdefault(category, set()).add(suppressed_line)


def ProcessGlobalSuppresions(lines):
  """Updates the list of global error suppressions.

  Parses any lint directives in the file that have global effect.

  Args:
    lines: An array of strings, each representing a line of the file, with the
           last element being empty if the file is terminated with a newline.
  """
  for line in lines:
    if _SEARCH_C_FILE.search(line):
      for category in _DEFAULT_C_SUPPRESSED_CATEGORIES:
        _global_error_suppressions[category] = True


def ResetNolintSuppressions():
  """Resets the set of NOLINT suppressions to empty."""
  _error_suppressions.clear()
  _global_error_suppressions.clear()


def IsErrorSuppressedByNolint(category, linenum):
  """Returns true if the specified error category is suppressed on this line.

  Consults the global error_suppressions map populated by
  ParseNolintSuppressions/ProcessGlobalSuppresions/ResetNolintSuppressions.

  Args:
    category: str, the category of the error.
    linenum: int, the current line number.
  Returns:
    bool, True iff the error should be suppressed due to a NOLINT comment or
    global suppression.
  """
  return (_global_error_suppressions.get(category, False) or
          linenum in _error_suppressions.get(category, set()) or
          linenum in _error_suppressions.get(None, set()))


def Match(pattern, s):
  """Matches the string with the pattern, caching the compiled regexp."""
  # The regexp compilation caching is inlined in both Match and Search for
  # performance reasons; factoring it out into a separate function turns out
  # to be noticeably expensive.
  if pattern not in _regexp_compile_cache:
    _regexp_compile_cache[pattern] = sre_compile.compile(pattern)
  return _regexp_compile_cache[pattern].match(s)


def Search(pattern, s):
  """Searches the string for the pattern, caching the compiled regexp."""
  if pattern not in _regexp_compile_cache:
    _regexp_compile_cache[pattern] = sre_compile.compile(pattern)
  return _regexp_compile_cache[pattern].search(s)


class _IncludeState(object):
  """Tracks line numbers for includes, and the order in which includes appear.

  include_list contains list of lists of (header, line number) pairs.
  It's a lists of lists rather than just one flat list to make it
  easier to update across preprocessor boundaries.

  Call CheckNextIncludeOrder() once for each header in the file, passing
  in the type constants defined above. Calls in an illegal order will
  raise an _IncludeError with an appropriate error message.

  """
  def __init__(self):
    self.include_list = [[]]
    self.ResetSection('')

  def ResetSection(self, directive):
    """Reset section checking for preprocessor directive.

    Args:
      directive: preprocessor directive (e.g. "if", "else").
    """
    # Update list of includes.  Note that we never pop from the
    # include list.
    if directive in ('if', 'ifdef', 'ifndef'):
      self.include_list.append([])
    elif directive in ('else', 'elif'):
      self.include_list[-1] = []


class _CppLintState(object):
  """Maintains module-wide state.."""

  def __init__(self):
    self.error_count = 0    # global count of reported errors
    self.errors_by_category = {}  # string to int dict storing error counts

  def ResetErrorCounts(self):
    """Sets the module's error statistic back to zero."""
    self.error_count = 0
    self.errors_by_category = {}

  def IncrementErrorCount(self, category):
    """Bumps the module's error statistic."""
    self.error_count += 1

  def PrintError(self, message):
    sys.stderr.write(message)

_cpplint_state = _CppLintState()


class _FunctionState(object):
  """Tracks current function name and the number of lines in its body."""

  _NORMAL_TRIGGER = 250  # for --v=0, 500 for --v=1, etc.
  _TEST_TRIGGER = 400    # about 50% more than _NORMAL_TRIGGER.

  def __init__(self):
    self.in_a_function = False
    self.lines_in_function = 0
    self.current_function = ''

  def Begin(self, function_name):
    """Start analyzing function body.

    Args:
      function_name: The name of the function being tracked.
    """
    self.in_a_function = True
    self.lines_in_function = 0
    self.current_function = function_name

  def Count(self):
    """Count line in current function body."""
    if self.in_a_function:
      self.lines_in_function += 1

  def Check(self, error, filename, linenum):
    """Report if too many lines in function body.

    Args:
      error: The function to call with any errors found.
      filename: The name of the current file.
      linenum: The number of the line to check.
    """
    if not self.in_a_function:
      return

    if Match(r'T(EST|est)', self.current_function):
      base_trigger = self._TEST_TRIGGER
    else:
      base_trigger = self._NORMAL_TRIGGER
    trigger = base_trigger * 2

    if self.lines_in_function > trigger:
      error_level = int(math.log(self.lines_in_function / base_trigger, 2))
      # 50 => 0, 100 => 1, 200 => 2, 400 => 3, 800 => 4, 1600 => 5, ...
      if error_level > 5:
        error_level = 5
      error(filename, linenum, 'readability/fn_size', error_level,
            'Small and focused functions are preferred:'
            ' %s has %d non-comment lines'
            ' (error triggered by exceeding %d lines).'  % (
                self.current_function, self.lines_in_function, trigger))

  def End(self):
    """Stop analyzing function body."""
    self.in_a_function = False


class FileInfo(object):
  """Provides utility functions for filenames.

  FileInfo provides easy access to the components of a file's path
  relative to the project root.
  """

  def __init__(self, filename):
    self._filename = filename

  def FullName(self):
    """Make Windows paths like Unix."""
    return os.path.abspath(self._filename).replace('\\', '/')

  def Extension(self):
    """File extension - text following the final period, includes that period."""
    return os.path.splitext(self.FullName())


def Error(filename, linenum, category, confidence, message):
  """Logs the fact we've found a lint error.

  We log where the error was found, and also our confidence in the error,
  that is, how certain we are this is a legitimate style regression, and
  not a misidentification or a use that's sometimes justified.

  False positives can be suppressed by the use of
  "cpplint(category)"  comments on the offending line.  These are
  parsed into _error_suppressions.

  Args:
    filename: The name of the file containing the error.
    linenum: The number of the line containing the error.
    category: A string used to describe the "category" this bug
      falls under: "whitespace", say, or "runtime".  Categories
      may have a hierarchy separated by slashes: "whitespace/indent".
    confidence: A number from 1-5 representing a confidence score for
      the error, with 5 meaning that we are certain of the problem,
      and 1 meaning that it could be a legitimate construct.
    message: The error message.
  """
  if not IsErrorSuppressedByNolint(category, linenum):
    _cpplint_state.IncrementErrorCount(category)
    final_message = '%s:%s:  %s  [%s] [%d]\n' % (
        filename, linenum, message, category, confidence)
    sys.stderr.write(final_message)

# Matches standard C++ escape sequences per 2.13.2.3 of the C++ standard.
_RE_PATTERN_CLEANSE_LINE_ESCAPES = regex.compile(
    r'\\([abfnrtv?"\\\']|\d+|x[0-9a-fA-F]+)')
# Match a single C style comment on the same line.
_RE_PATTERN_C_COMMENTS = r'/\*(?:[^*]|\*(?!/))*\*/'
# Matches multi-line C style comments.
# This RE is a little bit more complicated than one might expect, because we
# have to take care of space removals tools so we can handle comments inside
# statements better.
# The current rule is: We only clear spaces from both sides when we're at the
# end of the line. Otherwise, we try to remove spaces from the right side,
# if this doesn't work we try on left side but only if there's a non-character
# on the right.
_RE_PATTERN_CLEANSE_LINE_C_COMMENTS = regex.compile(
    r'(\s*' + _RE_PATTERN_C_COMMENTS + r'\s*$|' +
    _RE_PATTERN_C_COMMENTS + r'\s+|' +
    r'\s+' + _RE_PATTERN_C_COMMENTS + r'(?=\W)|' +
    _RE_PATTERN_C_COMMENTS + r')')


def IsCppString(line):
  """Does line terminate so, that the next symbol is in string constant.

  This function does not consider single-line nor multi-line comments.

  Args:
    line: is a partial line of code starting from the 0..n.

  Returns:
    True, if next character appended to 'line' is inside a
    string constant.
  """

  line = line.replace(r'\\', 'XX')  # after this, \\" does not match to \"
  return ((line.count('"') - line.count(r'\"') - line.count("'\"'")) & 1) == 1


def CleanseRawStrings(raw_lines):
  """Removes C++11 raw strings from lines.

    Before:
      static const char kData[] = R"(
          multi-line string
          )";

    After:
      static const char kData[] = ""
          (replaced by blank line)
          "";

  Args:
    raw_lines: list of raw lines.

  Returns:
    list of lines with C++11 raw strings replaced by empty strings.
  """

  delimiter = None
  lines_without_raw_strings = []
  for line in raw_lines:
    if delimiter:
      # Inside a raw string, look for the end
      end = line.find(delimiter)
      if end >= 0:
        # Found the end of the string, match leading space for this
        # line and resume copying the original lines, and also insert
        # a "" on the last line.
        leading_space = Match(r'^(\s*)\S', line)
        line = leading_space.group(1) + '""' + line[end + len(delimiter):]
        delimiter = None
      else:
        # Haven't found the end yet, append a blank line.
        line = '""'

    # Look for beginning of a raw string, and replace them with
    # empty strings.  This is done in a loop to handle multiple raw
    # strings on the same line.
    while delimiter is None:
      # Look for beginning of a raw string.
      # See 2.14.15 [lex.string] for syntax.
      #
      # Once we have matched a raw string, we check the prefix of the
      # line to make sure that the line is not part of a single line
      # comment.  It's done this way because we remove raw strings
      # before removing comments as opposed to removing comments
      # before removing raw strings.  This is because there are some
      # cpplint checks that requires the comments to be preserved, but
      # we don't want to check comments that are inside raw strings.
      matched = Match(r'^(.*?)\b(?:R|u8R|uR|UR|LR)"([^\s\\()]*)\((.*)$', line)
      if (matched and
          not Match(r'^([^\'"]|\'(\\.|[^\'])*\'|"(\\.|[^"])*")*//',
                    matched.group(1))):
        delimiter = ')' + matched.group(2) + '"'

        end = matched.group(3).find(delimiter)
        if end >= 0:
          # Raw string ended on same line
          line = (matched.group(1) + '""' +
                  matched.group(3)[end + len(delimiter):])
          delimiter = None
        else:
          # Start of a multi-line raw string
          line = matched.group(1) + '""'
      else:
        break

    lines_without_raw_strings.append(line)

  # TODO(unknown): if delimiter is not None here, we might want to
  # emit a warning for unterminated string.
  return lines_without_raw_strings


def FindNextMultiLineCommentStart(lines, lineix):
  """Find the beginning marker for a multiline comment."""
  while lineix < len(lines):
    if lines[lineix].strip().startswith('/*'):
      # Only return this marker if the comment goes beyond this line
      if lines[lineix].strip().find('*/', 2) < 0:
        return lineix
    lineix += 1
  return len(lines)


def FindNextMultiLineCommentEnd(lines, lineix):
  """We are inside a comment, find the end marker."""
  while lineix < len(lines):
    if lines[lineix].strip().endswith('*/'):
      return lineix
    lineix += 1
  return len(lines)


def RemoveMultiLineCommentsFromRange(lines, begin, end):
  """Clears a range of lines for multi-line comments."""
  # Having // dummy comments makes the lines non-empty, so we will not get
  # unnecessary blank line warnings later in the code.
  for i in range(begin, end):
    lines[i] = '/**/'


def RemoveMultiLineComments(filename, lines, error):
  """Removes multiline (c-style) comments from lines."""
  lineix = 0
  while lineix < len(lines):
    lineix_begin = FindNextMultiLineCommentStart(lines, lineix)
    if lineix_begin >= len(lines):
      return
    lineix_end = FindNextMultiLineCommentEnd(lines, lineix_begin)
    if lineix_end >= len(lines):
      error(filename, lineix_begin + 1, 'readability/multiline_comment', 5,
            'Could not find end of multi-line comment')
      return
    RemoveMultiLineCommentsFromRange(lines, lineix_begin, lineix_end + 1)
    lineix = lineix_end + 1


def CleanseComments(line):
  """Removes //-comments and single-line C-style /* */ comments.

  Args:
    line: A line of C++ source.

  Returns:
    The line with single-line comments removed.
  """
  commentpos = line.find('//')
  if commentpos != -1 and not IsCppString(line[:commentpos]):
    line = line[:commentpos].rstrip()
  # get rid of /* ... */
  return _RE_PATTERN_CLEANSE_LINE_C_COMMENTS.sub('', line)


class CleansedLines(object):
  """Holds 4 copies of all lines with different preprocessing applied to them.

  1) elided member contains lines without strings and comments.
  2) lines member contains lines without comments.
  3) raw_lines member contains all the lines without processing.
  4) lines_without_raw_strings member is same as raw_lines, but with C++11 raw
     strings removed.
  All these members are of <type 'list'>, and of the same length.
  """

  def __init__(self, lines):
    self.elided = []
    self.lines = []
    self.raw_lines = lines
    self.num_lines = len(lines)
    self.lines_without_raw_strings = CleanseRawStrings(lines)
    for linenum in range(len(self.lines_without_raw_strings)):
      self.lines.append(CleanseComments(
          self.lines_without_raw_strings[linenum]))
      elided = self._CollapseStrings(self.lines_without_raw_strings[linenum])
      self.elided.append(CleanseComments(elided))

  def NumLines(self):
    """Returns the number of lines represented."""
    return self.num_lines

  @staticmethod
  def _CollapseStrings(elided):
    """Collapses strings and chars on a line to simple "" or '' blocks.

    We nix strings first so we're not fooled by text like '"http://"'

    Args:
      elided: The line being processed.

    Returns:
      The line with collapsed strings.
    """
    if _RE_PATTERN_INCLUDE.match(elided):
      return elided

    # Remove escaped characters first to make quote/single quote collapsing
    # basic.  Things that look like escaped characters shouldn't occur
    # outside of strings and chars.
    elided = _RE_PATTERN_CLEANSE_LINE_ESCAPES.sub('', elided)

    # Replace quoted strings and digit separators.  Both single quotes
    # and double quotes are processed in the same loop, otherwise
    # nested quotes wouldn't work.
    collapsed = ''
    while True:
      # Find the first quote character
      match = Match(r'^([^\'"]*)([\'"])(.*)$', elided)
      if not match:
        collapsed += elided
        break
      head, quote, tail = match.groups()

      if quote == '"':
        # Collapse double quoted strings
        second_quote = tail.find('"')
        if second_quote >= 0:
          collapsed += head + '""'
          elided = tail[second_quote + 1:]
        else:
          # Unmatched double quote, don't bother processing the rest
          # of the line since this is probably a multiline string.
          collapsed += elided
          break
      else:
        # Found single quote, check nearby text to eliminate digit separators.
        #
        # There is no special handling for floating point here, because
        # the integer/fractional/exponent parts would all be parsed
        # correctly as long as there are digits on both sides of the
        # separator.  So we are fine as long as we don't see something
        # like "0.'3" (gcc 4.9.0 will not allow this literal).
        if Search(r'\b(?:0[bBxX]?|[1-9])[0-9a-fA-F]*$', head):
          match_literal = Match(r'^((?:\'?[0-9a-zA-Z_])*)(.*)$', "'" + tail)
          collapsed += head + match_literal.group(1).replace("'", '')
          elided = match_literal.group(2)
        else:
          second_quote = tail.find('\'')
          if second_quote >= 0:
            collapsed += head + "''"
            elided = tail[second_quote + 1:]
          else:
            # Unmatched single quote
            collapsed += elided
            break

    return collapsed


def FindEndOfExpressionInLine(line, startpos, stack):
  """Find the position just after the end of current parenthesized expression.

  Args:
    line: a CleansedLines line.
    startpos: start searching at this position.
    stack: nesting stack at startpos.

  Returns:
    On finding matching end: (index just after matching end, None)
    On finding an unclosed expression: (-1, None)
    Otherwise: (-1, new stack at end of this line)
  """
  for i in range(startpos, len(line)):
    char = line[i]
    if char in '([{':
      # Found start of parenthesized expression, push to expression stack
      stack.append(char)
    elif char == '<':
      # Found potential start of template argument list
      if i > 0 and line[i - 1] == '<':
        # Left shift operator
        if stack and stack[-1] == '<':
          stack.pop()
          if not stack:
            return (-1, None)
      elif i > 0 and Search(r'\boperator\s*$', line[0:i]):
        # operator<, don't add to stack
        continue
      else:
        # Tentative start of template argument list
        stack.append('<')
    elif char in ')]}':
      # Found end of parenthesized expression.
      #
      # If we are currently expecting a matching '>', the pending '<'
      # must have been an operator.  Remove them from expression stack.
      while stack and stack[-1] == '<':
        stack.pop()
      if not stack:
        return (-1, None)
      if ((stack[-1] == '(' and char == ')') or
          (stack[-1] == '[' and char == ']') or
          (stack[-1] == '{' and char == '}')):
        stack.pop()
        if not stack:
          return (i + 1, None)
      else:
        # Mismatched parentheses
        return (-1, None)
    elif char == '>':
      # Found potential end of template argument list.

      # Ignore "->" and operator functions
      if (i > 0 and
          (line[i - 1] == '-' or Search(r'\boperator\s*$', line[0:i - 1]))):
        continue

      # Pop the stack if there is a matching '<'.  Otherwise, ignore
      # this '>' since it must be an operator.
      if stack:
        if stack[-1] == '<':
          stack.pop()
          if not stack:
            return (i + 1, None)
    elif char == ';':
      # Found something that look like end of statements.  If we are currently
      # expecting a '>', the matching '<' must have been an operator, since
      # template argument list should not contain statements.
      while stack and stack[-1] == '<':
        stack.pop()
      if not stack:
        return (-1, None)

  # Did not find end of expression or unbalanced parentheses on this line
  return (-1, stack)


def CloseExpression(clean_lines, linenum, pos):
  """If input points to ( or { or [ or <, finds the position that closes it.

  If lines[linenum][pos] points to a '(' or '{' or '[' or '<', finds the
  linenum/pos that correspond to the closing of the expression.

  TODO(unknown): cpplint spends a fair bit of time matching parentheses.
  Ideally we would want to index all opening and closing parentheses once
  and have CloseExpression be just a simple lookup, but due to preprocessor
  tricks, this is not so easy.

  Args:
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    pos: A position on the line.

  Returns:
    A tuple (line, linenum, pos) pointer *past* the closing brace, or
    (line, len(lines), -1) if we never find a close.  Note we ignore
    strings and comments when matching; and the line we return is the
    'cleansed' line at linenum.
  """

  line = clean_lines.elided[linenum]
  if (line[pos] not in '({[<') or Match(r'<[<=]', line[pos:]):
    return (line, clean_lines.NumLines(), -1)

  # Check first line
  (end_pos, stack) = FindEndOfExpressionInLine(line, pos, [])
  if end_pos > -1:
    return (line, linenum, end_pos)

  # Continue scanning forward
  while stack and linenum < clean_lines.NumLines() - 1:
    linenum += 1
    line = clean_lines.elided[linenum]
    (end_pos, stack) = FindEndOfExpressionInLine(line, 0, stack)
    if end_pos > -1:
      return (line, linenum, end_pos)

  # Did not find end of expression before end of file, give up
  return (line, clean_lines.NumLines(), -1)


def FindStartOfExpressionInLine(line, endpos, stack):
  """Find position at the matching start of current expression.

  This is almost the reverse of FindEndOfExpressionInLine, but note
  that the input position and returned position differs by 1.

  Args:
    line: a CleansedLines line.
    endpos: start searching at this position.
    stack: nesting stack at endpos.

  Returns:
    On finding matching start: (index at matching start, None)
    On finding an unclosed expression: (-1, None)
    Otherwise: (-1, new stack at beginning of this line)
  """
  i = endpos
  while i >= 0:
    char = line[i]
    if char in ')]}':
      # Found end of expression, push to expression stack
      stack.append(char)
    elif char == '>':
      # Found potential end of template argument list.
      #
      # Ignore it if it's a "->" or ">=" or "operator>"
      if (i > 0 and
          (line[i - 1] == '-' or
           Match(r'\s>=\s', line[i - 1:]) or
           Search(r'\boperator\s*$', line[0:i]))):
        i -= 1
      else:
        stack.append('>')
    elif char == '<':
      # Found potential start of template argument list
      if i > 0 and line[i - 1] == '<':
        # Left shift operator
        i -= 1
      else:
        # If there is a matching '>', we can pop the expression stack.
        # Otherwise, ignore this '<' since it must be an operator.
        if stack and stack[-1] == '>':
          stack.pop()
          if not stack:
            return (i, None)
    elif char in '([{':
      # Found start of expression.
      #
      # If there are any unmatched '>' on the stack, they must be
      # operators.  Remove those.
      while stack and stack[-1] == '>':
        stack.pop()
      if not stack:
        return (-1, None)
      if ((char == '(' and stack[-1] == ')') or
          (char == '[' and stack[-1] == ']') or
          (char == '{' and stack[-1] == '}')):
        stack.pop()
        if not stack:
          return (i, None)
      else:
        # Mismatched parentheses
        return (-1, None)
    elif char == ';':
      # Found something that look like end of statements.  If we are currently
      # expecting a '<', the matching '>' must have been an operator, since
      # template argument list should not contain statements.
      while stack and stack[-1] == '>':
        stack.pop()
      if not stack:
        return (-1, None)

    i -= 1

  return (-1, stack)


def ReverseCloseExpression(clean_lines, linenum, pos):
  """If input points to ) or } or ] or >, finds the position that opens it.

  If lines[linenum][pos] points to a ')' or '}' or ']' or '>', finds the
  linenum/pos that correspond to the opening of the expression.

  Args:
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    pos: A position on the line.

  Returns:
    A tuple (line, linenum, pos) pointer *at* the opening brace, or
    (line, 0, -1) if we never find the matching opening brace.  Note
    we ignore strings and comments when matching; and the line we
    return is the 'cleansed' line at linenum.
  """
  line = clean_lines.elided[linenum]
  if line[pos] not in ')}]>':
    return (line, 0, -1)

  # Check last line
  (start_pos, stack) = FindStartOfExpressionInLine(line, pos, [])
  if start_pos > -1:
    return (line, linenum, start_pos)

  # Continue scanning backward
  while stack and linenum > 0:
    linenum -= 1
    line = clean_lines.elided[linenum]
    (start_pos, stack) = FindStartOfExpressionInLine(line, len(line) - 1, stack)
    if start_pos > -1:
      return (line, linenum, start_pos)

  # Did not find start of expression before beginning of file, give up
  return (line, 0, -1)


def GetIndentLevel(line):
  """Return the number of leading spaces in line.

  Args:
    line: A string to check.

  Returns:
    An integer count of leading spaces, possibly zero.
  """
  indent = Match(r'^( *)\S', line)
  if indent:
    return len(indent.group(1))
  else:
    return 0


def CheckForBadCharacters(filename, lines, error):
  """Logs an error for each line containing bad characters.

  Two kinds of bad characters:

  1. Unicode replacement characters: These indicate that either the file
  contained invalid UTF-8 (likely) or Unicode replacement characters (which
  it shouldn't).  Note that it's possible for this to throw off line
  numbering if the invalid UTF-8 occurred adjacent to a newline.

  2. NUL bytes.  These are problematic for some tools.

  Args:
    filename: The name of the current file.
    lines: An array of strings, each representing a line of the file.
    error: The function to call with any errors found.
  """
  for linenum, line in enumerate(lines):
    if unicode_escape_decode('\ufffd') in line:
      error(filename, linenum, 'readability/utf8', 5,
            'Line contains invalid UTF-8 (or Unicode replacement character).')
    if '\0' in line:
      error(filename, linenum, 'readability/nul', 5, 'Line contains NUL byte.')


def CheckForMultilineCommentsAndStrings(filename, clean_lines, linenum, error):
  """Logs an error if we see /* ... */ or "..." that extend past one line.

  /* ... */ comments are legit inside macros, for one line.
  Otherwise, we prefer // comments, so it's ok to warn about the
  other.  Likewise, it's ok for strings to extend across multiple
  lines, as long as a line continuation character (backslash)
  terminates each line. Although not currently prohibited by the C++
  style guide, it's ugly and unnecessary. We don't do well with either
  in this lint program, so we warn about both.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    error: The function to call with any errors found.
  """
  line = clean_lines.elided[linenum]

  # Remove all \\ (escaped backslashes) from the line. They are OK, and the
  # second (escaped) slash may trigger later \" detection erroneously.
  line = line.replace('\\\\', '')

  if line.count('/*') > line.count('*/'):
    error(filename, linenum, 'readability/multiline_comment', 5,
          'Complex multi-line /*...*/-style comment found. '
          'Lint may give bogus warnings.  '
          'Consider replacing these with //-style comments, '
          'with #if 0...#endif, '
          'or with more clearly structured multi-line comments.')

  if (line.count('"') - line.count('\\"')) % 2:
    error(filename, linenum, 'readability/multiline_string', 5,
          'Multi-line string ("...") found.  This lint script doesn\'t '
          'do well with such strings, and may give bogus warnings.  '
          'Use C++11 raw strings or concatenation instead.')


# Matches invalid increment: *count++, which moves pointer instead of
# incrementing a value.
_RE_PATTERN_INVALID_INCREMENT = regex.compile(
    r'^\s*\*\w+(\+\+|--);')


def CheckInvalidIncrement(filename, clean_lines, linenum, error):
  """Checks for invalid increment *count++.

  For example following function:
  void increment_counter(int* count) {
    *count++;
  }
  is invalid, because it effectively does count++, moving pointer, and should
  be replaced with ++*count, (*count)++ or *count += 1.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    error: The function to call with any errors found.
  """
  line = clean_lines.elided[linenum]
  if _RE_PATTERN_INVALID_INCREMENT.match(line):
    error(filename, linenum, 'runtime/invalid_increment', 5,
          'Changing pointer instead of value (or unused value of operator*).')


def IsMacroDefinition(clean_lines, linenum):
  if Search(r'^#define', clean_lines[linenum]):
    return True

  if linenum > 0 and Search(r'\\$', clean_lines[linenum - 1]):
    return True

  return False


def IsForwardClassDeclaration(clean_lines, linenum):
  return Match(r'^\s*(\btemplate\b)*.*class\s+\w+;\s*$', clean_lines[linenum])


class _BlockInfo(object):
  """Stores information about a generic block of code."""

  def __init__(self, linenum, seen_open_brace):
    self.starting_linenum = linenum
    self.seen_open_brace = seen_open_brace
    self.open_parentheses = 0
    self.inline_asm = _NO_ASM
    self.check_namespace_indentation = False

  def CheckBegin(self, filename, clean_lines, linenum, error):
    """Run checks that applies to text up to the opening brace.

    This is mostly for checking the text after the class identifier
    and the "{", usually where the base class is specified.  For other
    blocks, there isn't much to check, so we always pass.

    Args:
      filename: The name of the current file.
      clean_lines: A CleansedLines instance containing the file.
      linenum: The number of the line to check.
      error: The function to call with any errors found.
    """
    pass

  def CheckEnd(self, filename, clean_lines, linenum, error):
    """Run checks that applies to text after the closing brace.

    This is mostly used for checking end of namespace comments.

    Args:
      filename: The name of the current file.
      clean_lines: A CleansedLines instance containing the file.
      linenum: The number of the line to check.
      error: The function to call with any errors found.
    """
    pass

  def IsBlockInfo(self):
    """Returns true if this block is a _BlockInfo.

    This is convenient for verifying that an object is an instance of
    a _BlockInfo, but not an instance of any of the derived classes.

    Returns:
      True for this class, False for derived classes.
    """
    return self.__class__ == _BlockInfo


class _ExternCInfo(_BlockInfo):
  """Stores information about an 'extern "C"' block."""

  def __init__(self, linenum):
    _BlockInfo.__init__(self, linenum, True)


class _ClassInfo(_BlockInfo):
  """Stores information about a class."""

  def __init__(self, name, class_or_struct, clean_lines, linenum):
    _BlockInfo.__init__(self, linenum, False)
    self.name = name
    self.is_derived = False
    self.check_namespace_indentation = True
    if class_or_struct == 'struct':
      self.access = 'public'
      self.is_struct = True
    else:
      self.access = 'private'
      self.is_struct = False

    # Try to find the end of the class.  This will be confused by things like:
    #   class A {
    #   } *x = { ...
    #
    # But it's still good enough for CheckSectionSpacing.
    self.last_line = 0
    depth = 0
    for i in range(linenum, clean_lines.NumLines()):
      line = clean_lines.elided[i]
      depth += line.count('{') - line.count('}')
      if not depth:
        self.last_line = i
        break

  def CheckBegin(self, filename, clean_lines, linenum, error):
    # Look for a bare ':'
    if Search('(^|[^:]):($|[^:])', clean_lines.elided[linenum]):
      self.is_derived = True

  def CheckEnd(self, filename, clean_lines, linenum, error):
    # If there is a DISALLOW macro, it should appear near the end of
    # the class.
    seen_last_thing_in_class = False
    for i in range(linenum - 1, self.starting_linenum, -1):
      match = Search(
          r'\b(DISALLOW_COPY_AND_ASSIGN|DISALLOW_IMPLICIT_CONSTRUCTORS)\(' +
          self.name + r'\)',
          clean_lines.elided[i])
      if match:
        if seen_last_thing_in_class:
          error(filename, i, 'readability/constructors', 3,
                match.group(1) + ' should be the last thing in the class')
        break

      if not Match(r'^\s*$', clean_lines.elided[i]):
        seen_last_thing_in_class = True


class _NamespaceInfo(_BlockInfo):
  """Stores information about a namespace."""

  def __init__(self, name, linenum):
    _BlockInfo.__init__(self, linenum, False)
    self.name = name or ''
    self.check_namespace_indentation = True

  def CheckEnd(self, filename, clean_lines, linenum, error):
    """Check end of namespace comments."""
    line = clean_lines.raw_lines[linenum]

    # Check how many lines is enclosed in this namespace.  Don't issue
    # warning for missing namespace comments if there aren't enough
    # lines.  However, do apply checks if there is already an end of
    # namespace comment and it's incorrect.
    #
    # TODO(unknown): We always want to check end of namespace comments
    # if a namespace is large, but sometimes we also want to apply the
    # check if a short namespace contained nontrivial things (something
    # other than forward declarations).  There is currently no logic on
    # deciding what these nontrivial things are, so this check is
    # triggered by namespace size only, which works most of the time.
    if (linenum - self.starting_linenum < 10
        and not Match(r'^\s*};*\s*(//|/\*).*\bnamespace\b', line)):
      return

    # Look for matching comment at end of namespace.
    #
    # Note that we accept C style "/* */" comments for terminating
    # namespaces, so that code that terminate namespaces inside
    # preprocessor macros can be cpplint clean.
    #
    # We also accept stuff like "// end of namespace <name>." with the
    # period at the end.
    #
    # Besides these, we don't accept anything else, otherwise we might
    # get false negatives when existing comment is a substring of the
    # expected namespace.
    if self.name:
      # Named namespace
      if not Match((r'^\s*};*\s*(//|/\*).*\bnamespace\s+' +
                    regex.escape(self.name) + r'[\*/\.\\\s]*$'),
                   line):
        error(filename, linenum, 'readability/namespace', 5,
              'Namespace should be terminated with "// namespace %s"' %
              self.name)
    else:
      # Anonymous namespace
      if not Match(r'^\s*};*\s*(//|/\*).*\bnamespace[\*/\.\\\s]*$', line):
        # If "// namespace anonymous" or "// anonymous namespace (more text)",
        # mention "// anonymous namespace" as an acceptable form
        if Match(r'^\s*}.*\b(namespace anonymous|anonymous namespace)\b', line):
          error(filename, linenum, 'readability/namespace', 5,
                'Anonymous namespace should be terminated with "// namespace"'
                ' or "// anonymous namespace"')
        else:
          error(filename, linenum, 'readability/namespace', 5,
                'Anonymous namespace should be terminated with "// namespace"')


class _PreprocessorInfo(object):
  """Stores checkpoints of nesting stacks when #if/#else is seen."""

  def __init__(self, stack_before_if):
    # The entire nesting stack before #if
    self.stack_before_if = stack_before_if

    # The entire nesting stack up to #else
    self.stack_before_else = []

    # Whether we have already seen #else or #elif
    self.seen_else = False


class NestingState(object):
  """Holds states related to parsing braces."""

  def __init__(self):
    # Stack for tracking all braces.  An object is pushed whenever we
    # see a "{", and popped when we see a "}".  Only 3 types of
    # objects are possible:
    # - _ClassInfo: a class or struct.
    # - _NamespaceInfo: a namespace.
    # - _BlockInfo: some other type of block.
    self.stack = []

    # Top of the previous stack before each Update().
    #
    # Because the nesting_stack is updated at the end of each line, we
    # had to do some convoluted checks to find out what is the current
    # scope at the beginning of the line.  This check is simplified by
    # saving the previous top of nesting stack.
    #
    # We could save the full stack, but we only need the top.  Copying
    # the full nesting stack would slow down cpplint by ~10%.
    self.previous_stack_top = []

    # Stack of _PreprocessorInfo objects.
    self.pp_stack = []

  def SeenOpenBrace(self):
    """Check if we have seen the opening brace for the innermost block.

    Returns:
      True if we have seen the opening brace, False if the innermost
      block is still expecting an opening brace.
    """
    return (not self.stack) or self.stack[-1].seen_open_brace

  def InNamespaceBody(self):
    """Check if we are currently one level inside a namespace body.

    Returns:
      True if top of the stack is a namespace block, False otherwise.
    """
    return self.stack and isinstance(self.stack[-1], _NamespaceInfo)

  def InExternC(self):
    """Check if we are currently one level inside an 'extern "C"' block.

    Returns:
      True if top of the stack is an extern block, False otherwise.
    """
    return self.stack and isinstance(self.stack[-1], _ExternCInfo)

  def InClassDeclaration(self):
    """Check if we are currently one level inside a class or struct declaration.

    Returns:
      True if top of the stack is a class/struct, False otherwise.
    """
    return self.stack and isinstance(self.stack[-1], _ClassInfo)

  def InAsmBlock(self):
    """Check if we are currently one level inside an inline ASM block.

    Returns:
      True if the top of the stack is a block containing inline ASM.
    """
    return self.stack and self.stack[-1].inline_asm != _NO_ASM

  def InTemplateArgumentList(self, clean_lines, linenum, pos):
    """Check if current position is inside template argument list.

    Args:
      clean_lines: A CleansedLines instance containing the file.
      linenum: The number of the line to check.
      pos: position just after the suspected template argument.
    Returns:
      True if (linenum, pos) is inside template arguments.
    """
    while linenum < clean_lines.NumLines():
      # Find the earliest character that might indicate a template argument
      line = clean_lines.elided[linenum]
      match = Match(r'^[^{};=\[\]\.<>]*(.)', line[pos:])
      if not match:
        linenum += 1
        pos = 0
        continue
      token = match.group(1)
      pos += len(match.group(0))

      # These things do not look like template argument list:
      #   class Suspect {
      #   class Suspect x; }
      if token in ('{', '}', ';'): return False

      # These things look like template argument list:
      #   template <class Suspect>
      #   template <class Suspect = default_value>
      #   template <class Suspect[]>
      #   template <class Suspect...>
      if token in ('>', '=', '[', ']', '.'): return True

      # Check if token is an unmatched '<'.
      # If not, move on to the next character.
      if token != '<':
        pos += 1
        if pos >= len(line):
          linenum += 1
          pos = 0
        continue

      # We can't be sure if we just find a single '<', and need to
      # find the matching '>'.
      (_, end_line, end_pos) = CloseExpression(clean_lines, linenum, pos - 1)
      if end_pos < 0:
        # Not sure if template argument list or syntax error in file
        return False
      linenum = end_line
      pos = end_pos
    return False

  def UpdatePreprocessor(self, line):
    """Update preprocessor stack.

    We need to handle preprocessors due to classes like this:
      #ifdef SWIG
      struct ResultDetailsPageElementExtensionPoint {
      #else
      struct ResultDetailsPageElementExtensionPoint : public Extension {
      #endif

    We make the following assumptions (good enough for most files):
    - Preprocessor condition evaluates to true from #if up to first
      #else/#elif/#endif.

    - Preprocessor condition evaluates to false from #else/#elif up
      to #endif.  We still perform lint checks on these lines, but
      these do not affect nesting stack.

    Args:
      line: current line to check.
    """
    if Match(r'^\s*#\s*(if|ifdef|ifndef)\b', line):
      # Beginning of #if block, save the nesting stack here.  The saved
      # stack will allow us to restore the parsing state in the #else case.
      self.pp_stack.append(_PreprocessorInfo(copy.deepcopy(self.stack)))
    elif Match(r'^\s*#\s*(else|elif)\b', line):
      # Beginning of #else block
      if self.pp_stack:
        if not self.pp_stack[-1].seen_else:
          # This is the first #else or #elif block.  Remember the
          # whole nesting stack up to this point.  This is what we
          # keep after the #endif.
          self.pp_stack[-1].seen_else = True
          self.pp_stack[-1].stack_before_else = copy.deepcopy(self.stack)

        # Restore the stack to how it was before the #if
        self.stack = copy.deepcopy(self.pp_stack[-1].stack_before_if)
      else:
        # TODO(unknown): unexpected #else, issue warning?
        pass
    elif Match(r'^\s*#\s*endif\b', line):
      # End of #if or #else blocks.
      if self.pp_stack:
        # If we saw an #else, we will need to restore the nesting
        # stack to its former state before the #else, otherwise we
        # will just continue from where we left off.
        if self.pp_stack[-1].seen_else:
          # Here we can just use a shallow copy since we are the last
          # reference to it.
          self.stack = self.pp_stack[-1].stack_before_else
        # Drop the corresponding #if
        self.pp_stack.pop()
      else:
        # TODO(unknown): unexpected #endif, issue warning?
        pass

  # TODO(unknown): Update() is too long, but we will refactor later.
  def Update(self, filename, clean_lines, linenum, error):
    """Update nesting state with current line.

    Args:
      filename: The name of the current file.
      clean_lines: A CleansedLines instance containing the file.
      linenum: The number of the line to check.
      error: The function to call with any errors found.
    """
    line = clean_lines.elided[linenum]

    # Remember top of the previous nesting stack.
    #
    # The stack is always pushed/popped and not modified in place, so
    # we can just do a shallow copy instead of copy.deepcopy.  Using
    # deepcopy would slow down cpplint by ~28%.
    if self.stack:
      self.previous_stack_top = self.stack[-1]
    else:
      self.previous_stack_top = None

    # Update pp_stack
    self.UpdatePreprocessor(line)

    # Count parentheses.  This is to avoid adding struct arguments to
    # the nesting stack.
    if self.stack:
      inner_block = self.stack[-1]
      depth_change = line.count('(') - line.count(')')
      inner_block.open_parentheses += depth_change

      # Also check if we are starting or ending an inline assembly block.
      if inner_block.inline_asm in (_NO_ASM, _END_ASM):
        if (depth_change != 0 and
            inner_block.open_parentheses == 1 and
            _MATCH_ASM.match(line)):
          # Enter assembly block
          inner_block.inline_asm = _INSIDE_ASM
        else:
          # Not entering assembly block.  If previous line was _END_ASM,
          # we will now shift to _NO_ASM state.
          inner_block.inline_asm = _NO_ASM
      elif (inner_block.inline_asm == _INSIDE_ASM and
            inner_block.open_parentheses == 0):
        # Exit assembly block
        inner_block.inline_asm = _END_ASM

    # Consume namespace declaration at the beginning of the line.  Do
    # this in a loop so that we catch same line declarations like this:
    #   namespace proto2 { namespace bridge { class MessageSet; } }
    while True:
      # Match start of namespace.  The "\b\s*" below catches namespace
      # declarations even if it weren't followed by a whitespace, this
      # is so that we don't confuse our namespace checker.  The
      # missing spaces will be flagged by CheckSpacing.
      namespace_decl_match = Match(r'^\s*namespace\b\s*([:\w]+)?(.*)$', line)
      if not namespace_decl_match:
        break

      new_namespace = _NamespaceInfo(namespace_decl_match.group(1), linenum)
      self.stack.append(new_namespace)

      line = namespace_decl_match.group(2)
      if line.find('{') != -1:
        new_namespace.seen_open_brace = True
        line = line[line.find('{') + 1:]

    # Look for a class declaration in whatever is left of the line
    # after parsing namespaces.  The regexp accounts for decorated classes
    # such as in:
    #   class LOCKABLE API Object {
    #   };
    class_decl_match = Match(
        r'^(\s*(?:template\s*<[\w\s<>,:=]*>\s*)?'
        r'(class|struct)\s+(?:[A-Z_]+\s+)*(\w+(?:::\w+)*))'
        r'(.*)$', line)
    if (class_decl_match and
        (not self.stack or self.stack[-1].open_parentheses == 0)):
      # We do not want to accept classes that are actually template arguments:
      #   template <class Ignore1,
      #             class Ignore2 = Default<Args>,
      #             template <Args> class Ignore3>
      #   void Function() {};
      #
      # To avoid template argument cases, we scan forward and look for
      # an unmatched '>'.  If we see one, assume we are inside a
      # template argument list.
      end_declaration = len(class_decl_match.group(1))
      if not self.InTemplateArgumentList(clean_lines, linenum, end_declaration):
        self.stack.append(_ClassInfo(
            class_decl_match.group(3), class_decl_match.group(2),
            clean_lines, linenum))
        line = class_decl_match.group(4)

    # If we have not yet seen the opening brace for the innermost block,
    # run checks here.
    if not self.SeenOpenBrace():
      self.stack[-1].CheckBegin(filename, clean_lines, linenum, error)

    # Update access control if we are inside a class/struct
    if self.stack and isinstance(self.stack[-1], _ClassInfo):
      classinfo = self.stack[-1]
      access_match = Match(
          r'^(.*)\b(public|private|protected|signals)(\s+(?:slots\s*)?)?'
          r':(?:[^:]|$)',
          line)
      if access_match:
        classinfo.access = access_match.group(2)

    # Consume braces or semicolons from what's left of the line
    while True:
      # Match first brace, semicolon, or closed parenthesis.
      matched = Match(r'^[^{;)}]*([{;)}])(.*)$', line)
      if not matched:
        break

      token = matched.group(1)
      if token == '{':
        # If namespace or class hasn't seen a opening brace yet, mark
        # namespace/class head as complete.  Push a new block onto the
        # stack otherwise.
        if not self.SeenOpenBrace():
          self.stack[-1].seen_open_brace = True
        elif Match(r'^extern\s*"[^"]*"\s*\{', line):
          self.stack.append(_ExternCInfo(linenum))
        else:
          self.stack.append(_BlockInfo(linenum, True))
          if _MATCH_ASM.match(line):
            self.stack[-1].inline_asm = _BLOCK_ASM

      elif token == ';' or token == ')':
        # If we haven't seen an opening brace yet, but we already saw
        # a semicolon, this is probably a forward declaration.  Pop
        # the stack for these.
        #
        # Similarly, if we haven't seen an opening brace yet, but we
        # already saw a closing parenthesis, then these are probably
        # function arguments with extra "class" or "struct" keywords.
        # Also pop these stack for these.
        if not self.SeenOpenBrace():
          self.stack.pop()
      else:  # token == '}'
        # Perform end of block checks and pop the stack.
        if self.stack:
          self.stack[-1].CheckEnd(filename, clean_lines, linenum, error)
          self.stack.pop()
      line = matched.group(2)

  def InnermostClass(self):
    """Get class info on the top of the stack.

    Returns:
      A _ClassInfo object if we are inside a class, or None otherwise.
    """
    for i in range(len(self.stack), 0, -1):
      classinfo = self.stack[i - 1]
      if isinstance(classinfo, _ClassInfo):
        return classinfo
    return None


def CheckForNonStandardConstructs(filename, clean_lines, linenum,
                                  nesting_state, error):
  r"""Logs an error if we see certain non-ANSI constructs ignored by gcc-2.

  Complain about several constructs which gcc-2 accepts, but which are
  not standard C++.  Warning about these in lint is one way to ease the
  transition to new compilers.
  - put storage class first (e.g. "static const" instead of "const static").
  - "%lld" instead of %qd" in printf-type functions.
  - "%1$d" is non-standard in printf-type functions.
  - "\%" is an undefined character escape sequence.
  - text after #endif is not allowed.
  - invalid inner-style forward declaration.
  - >? and <? operators, and their >?= and <?= cousins.

  Additionally, check for constructor/destructor style violations and reference
  members, as it is very convenient to do so while checking for
  gcc-2 compliance.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    nesting_state: A NestingState instance which maintains information about
                   the current stack of nested blocks being parsed.
    error: A callable to which errors are reported, which takes 4 arguments:
           filename, line number, error level, and message
  """

  # Remove comments from the line, but leave in strings for now.
  line = clean_lines.lines[linenum]

  if Search(r'printf\s*\(.*".*%[-+ ]?\d*q', line):
    error(filename, linenum, 'runtime/printf_format', 3,
          '%q in format strings is deprecated.  Use %ll instead.')

  if Search(r'printf\s*\(.*".*%\d+\$', line):
    error(filename, linenum, 'runtime/printf_format', 2,
          '%N$ formats are unconventional.  Try rewriting to avoid them.')

  # Remove escaped backslashes before looking for undefined escapes.
  line = line.replace('\\\\', '')

  if Search(r'("|\').*\\(%|\[|\(|{)', line):
    error(filename, linenum, 'build/printf_format', 3,
          '%, [, (, and { are undefined character escapes.  Unescape them.')

  # For the rest, work with both comments and strings removed.
  line = clean_lines.elided[linenum]

  if Search(r'\b(const|volatile|void|char|short|int|long'
            r'|float|double|signed|unsigned'
            r'|schar|u?int8|u?int16|u?int32|u?int64)'
            r'\s+(register|static|extern|typedef)\b',
            line):
    error(filename, linenum, 'build/storage_class', 5,
          'Storage-class specifier (static, extern, typedef, etc) should be '
          'at the beginning of the declaration.')

  if Search(r'^\s*const\s*string\s*&\s*\w+\s*;', line):
    # TODO(unknown): Could it be expanded safely to arbitrary references,
    # without triggering too many false positives? The first
    # attempt triggered 5 warnings for mostly benign code in the regtest, hence
    # the restriction.
    # Here's the original regexp, for the reference:
    # type_name = r'\w+((\s*::\s*\w+)|(\s*<\s*\w+?\s*>))?'
    # r'\s*const\s*' + type_name + '\s*&\s*\w+\s*;'
    error(filename, linenum, 'runtime/member_string_references', 2,
          'const string& members are dangerous. It is much better to use '
          'alternatives, such as pointers or simple constants.')

  # Everything else in this function operates on class declarations.
  # Return early if the top of the nesting stack is not a class, or if
  # the class head is not completed yet.
  classinfo = nesting_state.InnermostClass()
  if not classinfo or not classinfo.seen_open_brace:
    return

  # The class may have been declared with namespace or classname qualifiers.
  # The constructor and destructor will not have those qualifiers.
  base_classname = classinfo.name.split('::')[-1]

  # Look for single-argument constructors that aren't marked explicit.
  # Technically a valid construct, but against style.
  explicit_constructor_match = Match(
      r'\s+(?:inline\s+)?(explicit\s+)?(?:inline\s+)?%s\s*'
      r'\(((?:[^()]|\([^()]*\))*)\)'
      % regex.escape(base_classname),
      line)

  if explicit_constructor_match:
    is_marked_explicit = explicit_constructor_match.group(1)

    if not explicit_constructor_match.group(2):
      constructor_args = []
    else:
      constructor_args = explicit_constructor_match.group(2).split(',')

    # collapse arguments so that commas in template parameter lists and function
    # argument parameter lists don't split arguments in two
    i = 0
    while i < len(constructor_args):
      constructor_arg = constructor_args[i]
      while (constructor_arg.count('<') > constructor_arg.count('>') or
             constructor_arg.count('(') > constructor_arg.count(')')):
        constructor_arg += ',' + constructor_args[i + 1]
        del constructor_args[i + 1]
      constructor_args[i] = constructor_arg
      i += 1

    variadic_args = [arg for arg in constructor_args if '&&...' in arg]
    defaulted_args = [arg for arg in constructor_args if '=' in arg]
    noarg_constructor = (not constructor_args or  # empty arg list
                         # 'void' arg specifier
                         (len(constructor_args) == 1 and
                          constructor_args[0].strip() == 'void'))
    onearg_constructor = ((len(constructor_args) == 1 and  # exactly one arg
                           not noarg_constructor) or
                          # all but at most one arg defaulted
                          (len(constructor_args) >= 1 and
                           not noarg_constructor and
                           len(defaulted_args) >= len(constructor_args) - 1) or
                          # variadic arguments with zero or one argument
                          (len(constructor_args) <= 2 and
                           len(variadic_args) >= 1))
    initializer_list_constructor = bool(
        onearg_constructor and
        Search(r'\bstd\s*::\s*initializer_list\b', constructor_args[0]))
    copy_constructor = bool(
        onearg_constructor and
        Match(r'(const\s+)?%s(\s*<[^>]*>)?(\s+const)?\s*(?:<\w+>\s*)?&'
              % regex.escape(base_classname), constructor_args[0].strip()))

    if (not is_marked_explicit and
        onearg_constructor and
        not initializer_list_constructor and
        not copy_constructor):
      if defaulted_args or variadic_args:
        error(filename, linenum, 'runtime/explicit', 5,
              'Constructors callable with one argument '
              'should be marked explicit.')
      else:
        error(filename, linenum, 'runtime/explicit', 5,
              'Single-parameter constructors should be marked explicit.')
    elif is_marked_explicit and not onearg_constructor:
      if noarg_constructor:
        error(filename, linenum, 'runtime/explicit', 5,
              'Zero-parameter constructors should not be marked explicit.')


def IsBlankLine(line):
  """Returns true if the given line is blank.

  We consider a line to be blank if the line is empty or consists of
  only white spaces.

  Args:
    line: A line of a string.

  Returns:
    True, if the given line is blank.
  """
  return not line or line.isspace()


def CheckForFunctionLengths(filename, clean_lines, linenum,
                            function_state, error):
  """Reports for long function bodies.

  For an overview why this is done, see:
  https://google-styleguide.googlecode.com/svn/trunk/cppguide.xml#Write_Short_Functions

  Uses a simplistic algorithm assuming other style guidelines
  (especially spacing) are followed.
  Only checks unindented functions, so class members are unchecked.
  Trivial bodies are unchecked, so constructors with huge initializer lists
  may be missed.
  Blank/comment lines are not counted so as to avoid encouraging the removal
  of vertical space and comments just to get through a lint check.
  NOLINT *on the last line of a function* disables this check.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    function_state: Current function name and lines in body so far.
    error: The function to call with any errors found.
  """
  lines = clean_lines.lines
  line = lines[linenum]
  joined_line = ''

  starting_func = False
  regexp = r'(\w(\w|::|\*|\&|\s)*)\('  # decls * & space::name( ...
  match_result = Match(regexp, line)
  if match_result:
    # If the name is all caps and underscores, figure it's a macro and
    # ignore it, unless it's TEST or TEST_F.
    function_name = match_result.group(1).split()[-1]
    if function_name == 'TEST' or function_name == 'TEST_F' or (
        not Match(r'[A-Z_]+$', function_name)):
      starting_func = True

  if starting_func:
    body_found = False
    for start_linenum in range(linenum, clean_lines.NumLines()):
      start_line = lines[start_linenum]
      joined_line += ' ' + start_line.lstrip()
      if Search(r'(;|})', start_line):  # Declarations and trivial functions
        body_found = True
        break                              # ... ignore
      elif Search(r'{', start_line):
        body_found = True
        function = Search(r'((\w|:)*)\(', line).group(1)
        if Match(r'TEST', function):    # Handle TEST... macros
          parameter_regexp = Search(r'(\(.*\))', joined_line)
          if parameter_regexp:             # Ignore bad syntax
            function += parameter_regexp.group(1)
        else:
          function += '()'
        function_state.Begin(function)
        break
    if not body_found:
      # No body for the function (or evidence of a non-function) was found.
      error(filename, linenum, 'readability/fn_size', 5,
            'Lint failed to find start of function body.')
  elif Match(r'^\}\s*$', line):  # function end
    function_state.Check(error, filename, linenum)
    function_state.End()
  elif not Match(r'^\s*$', line):
    function_state.Count()  # Count non-blank/non-comment lines.


_RE_PATTERN_TODO = regex.compile(r'^//(\s*)TODO(\(.+?\))?:?(\s|$)?')


def CheckComment(line, filename, linenum, next_line_start, error):
  """Checks for common mistakes in comments.

  Args:
    line: The line in question.
    filename: The name of the current file.
    linenum: The number of the line to check.
    next_line_start: The first non-whitespace column of the next line.
    error: The function to call with any errors found.
  """
  commentpos = line.find('//')
  if commentpos != -1:
    # Check if the // may be in quotes.  If so, ignore it
    if regex.sub(r'\\.', '', line[0:commentpos]).count('"') % 2 == 0:
      # Checks for common mistakes in TODO comments.
      comment = line[commentpos:]
      match = _RE_PATTERN_TODO.match(comment)
      if match:
        # One whitespace is correct; zero whitespace is handled elsewhere.
        leading_whitespace = match.group(1)
        if len(leading_whitespace) > 1:
          error(filename, linenum, 'whitespace/todo', 2,
                'Too many spaces before TODO')

      # If the comment contains an alphanumeric character, there
      # should be a space somewhere between it and the // unless
      # it's a /// or //! Doxygen comment.
      if (Match(r'//[^ ]*\w', comment) and
          not Match(r'(///|//\!)(\s+|$)', comment)):
        error(filename, linenum, 'whitespace/comments', 4,
              'Should have a space between // and comment')


def CheckSpacing(filename, clean_lines, linenum, nesting_state, error):
  """Checks for the correctness of various spacing issues in the code.

  Things we check for: spaces around operators, spaces after
  if/for/while/switch, no spaces around parens in function calls, two
  spaces between code and comment, don't start a block with a blank
  line, don't end a function with a blank line, don't add a blank line
  after public/protected/private, don't have too many blank lines in a row.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    nesting_state: A NestingState instance which maintains information about
                   the current stack of nested blocks being parsed.
    error: The function to call with any errors found.
  """

  # Don't use "elided" lines here, otherwise we can't check commented lines.
  # Don't want to use "raw" either, because we don't want to check inside C++11
  # raw strings,
  raw = clean_lines.lines_without_raw_strings
  line = raw[linenum]

  # Before nixing comments, check if the line is blank for no good
  # reason.  This includes the first line after a block is opened, and
  # blank lines at the end of a function (ie, right before a line like '}'
  #
  # Skip all the blank line checks if we are immediately inside a
  # namespace body.  In other words, don't issue blank line warnings
  # for this block:
  #   namespace {
  #
  #   }
  #
  # A warning about missing end of namespace comments will be issued instead.
  #
  # Also skip blank line checks for 'extern "C"' blocks, which are formatted
  # like namespaces.
  if (IsBlankLine(line) and
      not nesting_state.InNamespaceBody() and
      not nesting_state.InExternC()):
    elided = clean_lines.elided
    prev_line = elided[linenum - 1]
    prevbrace = prev_line.rfind('{')
    # TODO(unknown): Don't complain if line before blank line, and line after,
    #                both start with alnums and are indented the same amount.
    #                This ignores whitespace at the start of a namespace block
    #                because those are not usually indented.
    if prevbrace != -1 and prev_line[prevbrace:].find('}') == -1:
      # OK, we have a blank line at the start of a code block.  Before we
      # complain, we check if it is an exception to the rule: The previous
      # non-empty line has the parameters of a function header that are indented
      # 4 spaces (because they did not fit in a 80 column line when placed on
      # the same line as the function name).  We also check for the case where
      # the previous line is indented 6 spaces, which may happen when the
      # initializers of a constructor do not fit into a 80 column line.
      exception = False
      if Match(r' {6}\w', prev_line):  # Initializer list?
        # We are looking for the opening column of initializer list, which
        # should be indented 4 spaces to cause 6 space indentation afterwards.
        search_position = linenum-2
        while (search_position >= 0
               and Match(r' {6}\w', elided[search_position])):
          search_position -= 1
        exception = (search_position >= 0
                     and elided[search_position][:5] == '    :')
      else:
        # Search for the function arguments or an initializer list.  We use a
        # simple heuristic here: If the line is indented 4 spaces; and we have a
        # closing paren, without the opening paren, followed by an opening brace
        # or colon (for initializer lists) we assume that it is the last line of
        # a function header.  If we have a colon indented 4 spaces, it is an
        # initializer list.
        exception = (Match(r' {4}\w[^\(]*\)\s*(const\s*)?(\{\s*$|:)',
                           prev_line)
                     or Match(r' {4}:', prev_line))

      if not exception:
        error(filename, linenum, 'whitespace/blank_line', 2,
              'Redundant blank line at the start of a code block '
              'should be deleted.')
    # Ignore blank lines at the end of a block in a long if-else
    # chain, like this:
    #   if (condition1) {
    #     // Something followed by a blank line
    #
    #   } else if (condition2) {
    #     // Something else
    #   }
    if linenum + 1 < clean_lines.NumLines():
      next_line = raw[linenum + 1]
      if (next_line
          and Match(r'\s*}', next_line)
          and next_line.find('} else ') == -1):
        error(filename, linenum, 'whitespace/blank_line', 3,
              'Redundant blank line at the end of a code block '
              'should be deleted.')

    matched = Match(r'\s*(public|protected|private):', prev_line)
    if matched:
      error(filename, linenum, 'whitespace/blank_line', 3,
            'Do not leave a blank line after "%s:"' % matched.group(1))

  # Next, check comments
  next_line_start = 0
  if linenum + 1 < clean_lines.NumLines():
    next_line = raw[linenum + 1]
    next_line_start = len(next_line) - len(next_line.lstrip())
  CheckComment(line, filename, linenum, next_line_start, error)

  # get rid of comments and strings
  line = clean_lines.elided[linenum]


def _IsType(clean_lines, nesting_state, expr):
  """Check if expression looks like a type name, returns true if so.

  Args:
    clean_lines: A CleansedLines instance containing the file.
    nesting_state: A NestingState instance which maintains information about
                   the current stack of nested blocks being parsed.
    expr: The expression to check.
  Returns:
    True, if token looks like a type.
  """
  # Keep only the last token in the expression
  last_word = Match(r'^.*(\b\S+)$', expr)
  if last_word:
    token = last_word.group(1)
  else:
    token = expr

  # Match native types and stdint types
  if _TYPES.match(token):
    return True

  # Try a bit harder to match templated types.  Walk up the nesting
  # stack until we find something that resembles a typename
  # declaration for what we are looking for.
  typename_pattern = (r'\b(?:typename|class|struct)\s+' + regex.escape(token) +
                      r'\b')
  block_index = len(nesting_state.stack) - 1
  while block_index >= 0:
    if isinstance(nesting_state.stack[block_index], _NamespaceInfo):
      return False

    # Found where the opening brace is.  We want to scan from this
    # line up to the beginning of the function, minus a few lines.
    #   template <typename Type1,  // stop scanning here
    #             ...>
    #   class C
    #     : public ... {  // start scanning here
    last_line = nesting_state.stack[block_index].starting_linenum

    next_block_start = 0
    if block_index > 0:
      next_block_start = nesting_state.stack[block_index - 1].starting_linenum
    first_line = last_line
    while first_line >= next_block_start:
      if clean_lines.elided[first_line].find('template') >= 0:
        break
      first_line -= 1
    if first_line < next_block_start:
      # Didn't find any "template" keyword before reaching the next block,
      # there are probably no template things to check for this block
      block_index -= 1
      continue

    # Look for typename in the specified range
    for i in range(first_line, last_line + 1, 1):
      if Search(typename_pattern, clean_lines.elided[i]):
        return True
    block_index -= 1

  return False


def CheckBracesSpacing(filename, clean_lines, linenum, nesting_state, error):
  """Checks for horizontal spacing near commas.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    nesting_state: A NestingState instance which maintains information about
                   the current stack of nested blocks being parsed.
    error: The function to call with any errors found.
  """
  line = clean_lines.elided[linenum]

  # You shouldn't have a space before a semicolon at the end of the line.
  # There's a special case for "for" since the style guide allows space before
  # the semicolon there.
  if Search(r':\s*;\s*$', line):
    error(filename, linenum, 'whitespace/semicolon', 5,
          'Semicolon defining empty statement. Use {} instead.')
  elif Search(r'^\s*;\s*$', line):
    error(filename, linenum, 'whitespace/semicolon', 5,
          'Line contains only semicolon. If this should be an empty statement, '
          'use {} instead.')
  elif (Search(r'\s+;\s*$', line) and
        not Search(r'\bfor\b', line)):
    error(filename, linenum, 'whitespace/semicolon', 5,
          'Extra space before last semicolon. If this should be an empty '
          'statement, use {} instead.')


def CheckSectionSpacing(filename, clean_lines, class_info, linenum, error):
  """Checks for additional blank line issues related to sections.

  Currently the only thing checked here is blank line before protected/private.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    class_info: A _ClassInfo objects.
    linenum: The number of the line to check.
    error: The function to call with any errors found.
  """
  # Skip checks if the class is small, where small means 25 lines or less.
  # 25 lines seems like a good cutoff since that's the usual height of
  # terminals, and any class that can't fit in one screen can't really
  # be considered "small".
  #
  # Also skip checks if we are on the first line.  This accounts for
  # classes that look like
  #   class Foo { public: ... };
  #
  # If we didn't find the end of the class, last_line would be zero,
  # and the check will be skipped by the first condition.
  if (class_info.last_line - class_info.starting_linenum <= 24 or
      linenum <= class_info.starting_linenum):
    return

  matched = Match(r'\s*(public|protected|private):', clean_lines.lines[linenum])
  if matched:
    # Issue warning if the line before public/protected/private was
    # not a blank line, but don't do this if the previous line contains
    # "class" or "struct".  This can happen two ways:
    #  - We are at the beginning of the class.
    #  - We are forward-declaring an inner class that is semantically
    #    private, but needed to be public for implementation reasons.
    # Also ignores cases where the previous line ends with a backslash as can be
    # common when defining classes in C macros.
    prev_line = clean_lines.lines[linenum - 1]
    if (not IsBlankLine(prev_line) and
        not Search(r'\b(class|struct)\b', prev_line) and
        not Search(r'\\$', prev_line)):
      # Try a bit harder to find the beginning of the class.  This is to
      # account for multi-line base-specifier lists, e.g.:
      #   class Derived
      #       : public Base {
      end_class_head = class_info.starting_linenum
      for i in range(class_info.starting_linenum, linenum):
        if Search(r'\{\s*$', clean_lines.lines[i]):
          end_class_head = i
          break
      if end_class_head < linenum - 1:
        error(filename, linenum, 'whitespace/blank_line', 3,
              '"%s:" should be preceded by a blank line' % matched.group(1))


def GetPreviousNonBlankLine(clean_lines, linenum):
  """Return the most recent non-blank line and its line number.

  Args:
    clean_lines: A CleansedLines instance containing the file contents.
    linenum: The number of the line to check.

  Returns:
    A tuple with two elements.  The first element is the contents of the last
    non-blank line before the current line, or the empty string if this is the
    first non-blank line.  The second is the line number of that line, or -1
    if this is the first non-blank line.
  """

  prevlinenum = linenum - 1
  while prevlinenum >= 0:
    prevline = clean_lines.elided[prevlinenum]
    if not IsBlankLine(prevline):     # if not a blank line...
      return (prevline, prevlinenum)
    prevlinenum -= 1
  return ('', -1)


def CheckBraces(filename, clean_lines, linenum, error):
  """Looks for misplaced braces (e.g. at the end of line).

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    error: The function to call with any errors found.
  """

  line = clean_lines.elided[linenum]        # get rid of comments and strings

  # If braces come on one side of an else, they should be on both.
  # However, we have to worry about "else if" that spans multiple lines!
  if Search(r'else if(\s+constexpr)?\s*\(', line):  # could be multi-line if
    brace_on_left = bool(Search(r'}\s*else if(\s+constexpr)?\s*\(', line))
    # find the ( after the if
    pos = line.find('else if')
    pos = line.find('(', pos)
    if pos > 0:
      (endline, _, endpos) = CloseExpression(clean_lines, linenum, pos)
      brace_on_right = endline[endpos:].find('{') != -1
      if brace_on_left != brace_on_right:    # must be brace after if
        error(filename, linenum, 'readability/braces', 5,
              'If an else has a brace on one side, it should have it on both')
  elif Search(r'}\s*else[^{]*$', line) or Match(r'[^}]*else\s*{', line):
    error(filename, linenum, 'readability/braces', 5,
          'If an else has a brace on one side, it should have it on both')

  # Likewise, an else should never have the else clause on the same line
  if Search(r'\belse [^\s{]', line) and not Search(r'\belse if\b', line):
    error(filename, linenum, 'whitespace/newline', 4,
          'Else clause should never be on same line as else (use 2 lines)')

  # In the same way, a do/while should never be on one line
  if Match(r'\s*do [^\s{]', line):
    error(filename, linenum, 'whitespace/newline', 4,
          'do/while clauses should not be on a single line')

  # Check single-line if/else bodies. The style guide says 'curly braces are not
  # required for single-line statements'. We additionally allow multi-line,
  # single statements, but we reject anything with more than one semicolon in
  # it. This means that the first semicolon after the if should be at the end of
  # its line, and the line after that should have an indent level equal to or
  # lower than the if. We also check for ambiguous if/else nesting without
  # braces.
  if_else_match = Search(r'\b(if(\s+constexpr)?\s*\(|else\b)', line)
  if if_else_match and not Match(r'\s*#', line):
    if_indent = GetIndentLevel(line)
    endline, endlinenum, endpos = line, linenum, if_else_match.end()
    if_match = Search(r'\bif(\s+constexpr)?\s*\(', line)
    if if_match:
      # This could be a multiline if condition, so find the end first.
      pos = if_match.end() - 1
      (endline, endlinenum, endpos) = CloseExpression(clean_lines, linenum, pos)
    # Check for an opening brace, either directly after the if or on the next
    # line. If found, this isn't a single-statement conditional.
    if (not Match(r'\s*{', endline[endpos:])
        and not (Match(r'\s*$', endline[endpos:])
                 and endlinenum < (len(clean_lines.elided) - 1)
                 and Match(r'\s*{', clean_lines.elided[endlinenum + 1]))):
      while (endlinenum < len(clean_lines.elided)
             and ';' not in clean_lines.elided[endlinenum][endpos:]):
        endlinenum += 1
        endpos = 0
      if endlinenum < len(clean_lines.elided):
        endline = clean_lines.elided[endlinenum]
        # We allow a mix of whitespace and closing braces (e.g. for one-liner
        # methods) and a single \ after the semicolon (for macros)
        endpos = endline.find(';')
        if not Match(r';[\s}]*(\\?)$', endline[endpos:]):
          # Semicolon isn't the last character, there's something trailing.
          # Output a warning if the semicolon is not contained inside
          # a lambda expression.
          if not Match(r'^[^{};]*\[[^\[\]]*\][^{}]*\{[^{}]*\}\s*\)*[;,]\s*$',
                       endline):
            error(filename, linenum, 'readability/braces', 4,
                  'If/else bodies with multiple statements require braces')
        elif endlinenum < len(clean_lines.elided) - 1:
          # Make sure the next line is dedented
          next_line = clean_lines.elided[endlinenum + 1]
          next_indent = GetIndentLevel(next_line)
          # With ambiguous nested if statements, this will error out on the
          # if that *doesn't* match the else, regardless of whether it's the
          # inner one or outer one.
          if (if_match and Match(r'\s*else\b', next_line)
              and next_indent != if_indent):
            error(filename, linenum, 'readability/braces', 4,
                  'Else clause should be indented at the same level as if. '
                  'Ambiguous nested if/else chains require braces.')
          elif next_indent > if_indent:
            error(filename, linenum, 'readability/braces', 4,
                  'If/else bodies with multiple statements require braces')


def CheckTrailingSemicolon(filename, clean_lines, linenum, error):
  """Looks for redundant trailing semicolon.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    error: The function to call with any errors found.
  """

  line = clean_lines.elided[linenum]

  # Block bodies should not be followed by a semicolon.  Due to C++11
  # brace initialization, there are more places where semicolons are
  # required than not, so we use a whitelist approach to check these
  # rather than a blacklist.  These are the places where "};" should
  # be replaced by just "}":
  # 1. Some flavor of block following closing parenthesis:
  #    for (;;) {};
  #    while (...) {};
  #    switch (...) {};
  #    Function(...) {};
  #    if (...) {};
  #    if (...) else if (...) {};
  #
  # 2. else block:
  #    if (...) else {};
  #
  # 3. const member function:
  #    Function(...) const {};
  #
  # 4. Block following some statement:
  #    x = 42;
  #    {};
  #
  # 5. Block at the beginning of a function:
  #    Function(...) {
  #      {};
  #    }
  #
  #    Note that naively checking for the preceding "{" will also match
  #    braces inside multi-dimensional arrays, but this is fine since
  #    that expression will not contain semicolons.
  #
  # 6. Block following another block:
  #    while (true) {}
  #    {};
  #
  # 7. End of namespaces:
  #    namespace {};
  #
  # 8. End of requires expression:
  #    concept name = requires () {};
  #
  #    These semicolons seems far more common than other kinds of
  #    redundant semicolons, possibly due to people converting classes
  #    to namespaces.  For now we do not warn for this case.
  #
  # Try matching case 1 first.
  match = Match(r'^(.*\)\s*)\{', line)
  if match:
    # Matched closing parenthesis (case 1).  Check the token before the
    # matching opening parenthesis, and don't warn if it looks like a
    # macro.  This avoids these false positives:
    #  - macro that defines a base class
    #  - multi-line macro that defines a base class
    #  - macro that defines the whole class-head
    #
    # But we still issue warnings for macros that we know are safe to
    # warn, specifically:
    #  - TEST, TEST_F, TEST_P, MATCHER, MATCHER_P
    #  - TYPED_TEST
    #  - INTERFACE_DEF
    #  - EXCLUSIVE_LOCKS_REQUIRED, SHARED_LOCKS_REQUIRED, LOCKS_EXCLUDED:
    #
    # We implement a whitelist of safe macros instead of a blacklist of
    # unsafe macros, even though the latter appears less frequently in
    # google code and would have been easier to implement.  This is because
    # the downside for getting the whitelist wrong means some extra
    # semicolons, while the downside for getting the blacklist wrong
    # would result in compile errors.
    #
    # In addition to macros, we also don't want to warn on
    #  - Compound literals
    #  - Lambdas
    #  - alignas specifier with anonymous structs
    #  - decltype
    closing_brace_pos = match.group(1).rfind(')')
    opening_parenthesis = ReverseCloseExpression(
        clean_lines, linenum, closing_brace_pos)
    if opening_parenthesis[2] > -1:
      line_prefix = opening_parenthesis[0][0:opening_parenthesis[2]]
      macro = Search(r'\b([A-Z_][A-Z0-9_]*)\s*$', line_prefix)
      func = Match(r'^(.*\])\s*$', line_prefix)
      if ((macro and
           macro.group(1) not in (
               'TEST', 'TEST_F', 'MATCHER', 'MATCHER_P', 'TYPED_TEST',
               'EXCLUSIVE_LOCKS_REQUIRED', 'SHARED_LOCKS_REQUIRED',
               'LOCKS_EXCLUDED', 'INTERFACE_DEF')) or
          (func and not Search(r'\boperator\s*\[\s*\]', func.group(1))) or
          Search(r'\b(?:struct|union)\s+alignas\s*$', line_prefix) or
          Search(r'\bdecltype$', line_prefix) or
          Search(r'\s+=\s*$', line_prefix) or
          Search(r'\brequires$', line_prefix)):
        match = None
    if (match and
        opening_parenthesis[1] > 1 and
        Search(r'\]\s*$', clean_lines.elided[opening_parenthesis[1] - 1])):
      # Multi-line lambda-expression
      match = None

  else:
    # Try matching cases 2-3.
    match = Match(r'^(.*(?:else|\)\s*const)\s*)\{', line)
    if not match:
      # Try matching cases 4-6.  These are always matched on separate lines.
      #
      # Note that we can't simply concatenate the previous line to the
      # current line and do a single match, otherwise we may output
      # duplicate warnings for the blank line case:
      #   if (cond) {
      #     // blank line
      #   }
      prevline = GetPreviousNonBlankLine(clean_lines, linenum)[0]
      if prevline and Search(r'[;{}]\s*$', prevline):
        match = Match(r'^(\s*)\{', line)

  # Check matching closing brace
  if match:
    (endline, endlinenum, endpos) = CloseExpression(
        clean_lines, linenum, len(match.group(1)))
    if endpos > -1 and Match(r'^\s*;', endline[endpos:]):
      # Current {} pair is eligible for semicolon check, and we have found
      # the redundant semicolon, output warning here.
      #
      # Note: because we are scanning forward for opening braces, and
      # outputting warnings for the matching closing brace, if there are
      # nested blocks with trailing semicolons, we will get the error
      # messages in reversed order.

      # We need to check the line forward for NOLINT
      raw_lines = clean_lines.raw_lines
      ParseNolintSuppressions(filename, raw_lines[endlinenum-1], endlinenum-1,
                              error)
      ParseNolintSuppressions(filename, raw_lines[endlinenum], endlinenum,
                              error)

      error(filename, endlinenum, 'readability/braces', 4,
            "You don't need a ; after a }")


def CheckEmptyBlockBody(filename, clean_lines, linenum, error):
  """Look for empty loop/conditional body with only a single semicolon.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    error: The function to call with any errors found.
  """

  # Search for loop keywords at the beginning of the line.  Because only
  # whitespaces are allowed before the keywords, this will also ignore most
  # do-while-loops, since those lines should start with closing brace.
  #
  # We also check "if" blocks here, since an empty conditional block
  # is likely an error.
  line = clean_lines.elided[linenum]
  matched = Match(r'\s*(for|while|if)\s*\(', line)
  if matched:
    # Find the end of the conditional expression.
    (end_line, end_linenum, end_pos) = CloseExpression(
        clean_lines, linenum, line.find('('))

    # Output warning if what follows the condition expression is a semicolon.
    # No warning for all other cases, including whitespace or newline, since we
    # have a separate check for semicolons preceded by whitespace.
    if end_pos >= 0 and Match(r';', end_line[end_pos:]):
      if matched.group(1) == 'if':
        error(filename, end_linenum, 'whitespace/empty_conditional_body', 5,
              'Empty conditional bodies should use {}')
      else:
        error(filename, end_linenum, 'whitespace/empty_loop_body', 5,
              'Empty loop bodies should use {} or continue')

    # Check for if statements that have completely empty bodies (no comments)
    # and no else clauses.
    if end_pos >= 0 and matched.group(1) == 'if':
      # Find the position of the opening { for the if statement.
      # Return without logging an error if it has no brackets.
      opening_linenum = end_linenum
      opening_line_fragment = end_line[end_pos:]
      # Loop until EOF or find anything that's not whitespace or opening {.
      while not Search(r'^\s*\{', opening_line_fragment):
        if Search(r'^(?!\s*$)', opening_line_fragment):
          # Conditional has no brackets.
          return
        opening_linenum += 1
        if opening_linenum == len(clean_lines.elided):
          # Couldn't find conditional's opening { or any code before EOF.
          return
        opening_line_fragment = clean_lines.elided[opening_linenum]
      # Set opening_line (opening_line_fragment may not be entire opening line).
      opening_line = clean_lines.elided[opening_linenum]

      # Find the position of the closing }.
      opening_pos = opening_line_fragment.find('{')
      if opening_linenum == end_linenum:
        # We need to make opening_pos relative to the start of the entire line.
        opening_pos += end_pos
      (closing_line, closing_linenum, closing_pos) = CloseExpression(
          clean_lines, opening_linenum, opening_pos)
      if closing_pos < 0:
        return

      # Now construct the body of the conditional. This consists of the portion
      # of the opening line after the {, all lines until the closing line,
      # and the portion of the closing line before the }.
      if (clean_lines.raw_lines[opening_linenum] !=
          CleanseComments(clean_lines.raw_lines[opening_linenum])):
        # Opening line ends with a comment, so conditional isn't empty.
        return
      if closing_linenum > opening_linenum:
        # Opening line after the {. Ignore comments here since we checked above.
        bodylist = list(opening_line[opening_pos+1:])
        # All lines until closing line, excluding closing line, with comments.
        bodylist.extend(clean_lines.raw_lines[opening_linenum+1:closing_linenum])
        # Closing line before the }. Won't (and can't) have comments.
        bodylist.append(clean_lines.elided[closing_linenum][:closing_pos-1])
        body = '\n'.join(bodylist)
      else:
        # If statement has brackets and fits on a single line.
        body = opening_line[opening_pos+1:closing_pos-1]

      # Check if the body is empty
      if not _EMPTY_CONDITIONAL_BODY_PATTERN.search(body):
        return
      # The body is empty. Now make sure there's not an else clause.
      current_linenum = closing_linenum
      current_line_fragment = closing_line[closing_pos:]
      # Loop until EOF or find anything that's not whitespace or else clause.
      while Search(r'^\s*$|^(?=\s*else)', current_line_fragment):
        if Search(r'^(?=\s*else)', current_line_fragment):
          # Found an else clause, so don't log an error.
          return
        current_linenum += 1
        if current_linenum == len(clean_lines.elided):
          break
        current_line_fragment = clean_lines.elided[current_linenum]

      # The body is empty and there's no else clause until EOF or other code.
      error(filename, end_linenum, 'whitespace/empty_if_body', 4,
            ('If statement had no body and no else clause'))


def CheckAltTokens(filename, clean_lines, linenum, error):
  """Check alternative keywords being used in boolean expressions.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    error: The function to call with any errors found.
  """
  line = clean_lines.elided[linenum]

  # Avoid preprocessor lines
  if Match(r'^\s*#', line):
    return

  # Last ditch effort to avoid multi-line comments.  This will not help
  # if the comment started before the current line or ended after the
  # current line, but it catches most of the false positives.  At least,
  # it provides a way to workaround this warning for people who use
  # multi-line comments in preprocessor macros.
  #
  # TODO(unknown): remove this once cpplint has better support for
  # multi-line comments.
  if line.find('/*') >= 0 or line.find('*/') >= 0:
    return

  for match in _ALT_TOKEN_REPLACEMENT_PATTERN.finditer(line):
    error(filename, linenum, 'readability/alt_tokens', 2,
          'Use operator %s instead of %s' % (
              _ALT_TOKEN_REPLACEMENT[match.group(1)], match.group(1)))


def CheckStyle(filename, clean_lines, linenum, is_header, nesting_state,
               error):
  """Checks rules from the 'C++ style rules' section of cppguide.html.

  Most of these rules are hard to test (naming, comment style), but we
  do what we can.  In particular we check for 2-space indents, line lengths,
  tab usage, spaces inside code, etc.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    is_header: Whether file is header.
    nesting_state: A NestingState instance which maintains information about
                   the current stack of nested blocks being parsed.
    error: The function to call with any errors found.
  """

  # Don't use "elided" lines here, otherwise we can't check commented lines.
  # Don't want to use "raw" either, because we don't want to check inside C++11
  # raw strings,
  raw_lines = clean_lines.lines_without_raw_strings
  line = raw_lines[linenum]
  prev = raw_lines[linenum - 1] if linenum > 0 else ''

  # One or three blank spaces at the beginning of the line is weird; it's
  # hard to reconcile that with 2-space indents.
  # NOTE: here are the conditions rob pike used for his tests.  Mine aren't
  # as sophisticated, but it may be worth becoming so:  RLENGTH==initial_spaces
  # if(RLENGTH > 20) complain = 0;
  # if(match($0, " +(error|private|public|protected):")) complain = 0;
  # if(match(prev, "&& *$")) complain = 0;
  # if(match(prev, "\\|\\| *$")) complain = 0;
  # if(match(prev, "[\",=><] *$")) complain = 0;
  # if(match($0, " <<")) complain = 0;
  # if(match(prev, " +for \\(")) complain = 0;
  # if(prevodd && match(prevprev, " +for \\(")) complain = 0;
  classinfo = nesting_state.InnermostClass()
  cleansed_line = clean_lines.elided[linenum]

  # Some more style checks
  CheckBraces(filename, clean_lines, linenum, error)
  CheckTrailingSemicolon(filename, clean_lines, linenum, error)
  CheckEmptyBlockBody(filename, clean_lines, linenum, error)
  CheckSpacing(filename, clean_lines, linenum, nesting_state, error)
  CheckBracesSpacing(filename, clean_lines, linenum, nesting_state, error)
  CheckAltTokens(filename, clean_lines, linenum, error)
  classinfo = nesting_state.InnermostClass()
  if classinfo:
    CheckSectionSpacing(filename, clean_lines, classinfo, linenum, error)


_RE_PATTERN_INCLUDE = regex.compile(r'^\s*#\s*include\s*([<"])([^>"]*)[>"].*$')
# Matches the first component of a filename delimited by -s and _s. That is:
#  _RE_FIRST_COMPONENT.match('foo').group(0) == 'foo'
#  _RE_FIRST_COMPONENT.match('foo.cc').group(0) == 'foo'
#  _RE_FIRST_COMPONENT.match('foo-bar_baz.cc').group(0) == 'foo'
#  _RE_FIRST_COMPONENT.match('foo_bar-baz.cc').group(0) == 'foo'
_RE_FIRST_COMPONENT = regex.compile(r'^[^-_.]+')


def CheckIncludeLine(filename, clean_lines, linenum, include_state, error):
  """Check rules that are applicable to #include lines.

  Strings on #include lines are NOT removed from elided line, to make
  certain tasks easier. However, to prevent false positives, checks
  applicable to #include lines in CheckLanguage must be put here.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    include_state: An _IncludeState instance in which the headers are inserted.
    error: The function to call with any errors found.
  """
  fileinfo = FileInfo(filename)
  line = clean_lines.lines[linenum]

  # we shouldn't include a file more than once. actually, there are a
  # handful of instances where doing so is okay, but in general it's
  # not.
  match = _RE_PATTERN_INCLUDE.search(line)
  if match:
    include = match.group(2)
    is_system = (match.group(1) == '<')

    if not _THIRD_PARTY_HEADERS_PATTERN.match(include):
      include_state.include_list[-1].append((include, linenum))


def _GetTextInside(text, start_pattern):
  r"""Retrieves all the text between matching open and close parentheses.

  Given a string of lines and a regular expression string, retrieve all the text
  following the expression and between opening punctuation symbols like
  (, [, or {, and the matching close-punctuation symbol. This properly nested
  occurrences of the punctuations, so for the text like
    printf(a(), b(c()));
  a call to _GetTextInside(text, r'printf\(') will return 'a(), b(c())'.
  start_pattern must match string having an open punctuation symbol at the end.

  Args:
    text: The lines to extract text. Its comments and strings must be elided.
           It can be single line and can span multiple lines.
    start_pattern: The regexp string indicating where to start extracting
                   the text.
  Returns:
    The extracted text.
    None if either the opening string or ending punctuation could not be found.
  """
  # TODO(unknown): Audit cpplint.py to see what places could be profitably
  # rewritten to use _GetTextInside (and use inferior regexp matching today).

  # Give opening punctuations to get the matching close-punctuations.
  matching_punctuation = {'(': ')', '{': '}', '[': ']'}
  closing_punctuation = set(itervalues(matching_punctuation))

  # Find the position to start extracting text.
  match = regex.search(start_pattern, text, regex.M)
  if not match:  # start_pattern not found in text.
    return None
  start_position = match.end(0)

  assert start_position > 0, (
      'start_pattern must ends with an opening punctuation.')
  assert text[start_position - 1] in matching_punctuation, (
      'start_pattern must ends with an opening punctuation.')
  # Stack of closing punctuations we expect to have in text after position.
  punctuation_stack = [matching_punctuation[text[start_position - 1]]]
  position = start_position
  while punctuation_stack and position < len(text):
    if text[position] == punctuation_stack[-1]:
      punctuation_stack.pop()
    elif text[position] in closing_punctuation:
      # A closing punctuation without matching opening punctuations.
      return None
    elif text[position] in matching_punctuation:
      punctuation_stack.append(matching_punctuation[text[position]])
    position += 1
  if punctuation_stack:
    # Opening punctuations left without matching close-punctuations.
    return None
  # punctuations match.
  return text[start_position:position - 1]


# Patterns for matching call-by-reference parameters.
#
# Supports nested templates up to 2 levels deep using this messy pattern:
#   < (?: < (?: < [^<>]*
#               >
#           |   [^<>] )*
#         >
#     |   [^<>] )*
#   >
_RE_PATTERN_IDENT = r'[_a-zA-Z]\w*'  # =~ [[:alpha:]][[:alnum:]]*
_RE_PATTERN_TYPE = (
    r'(?:const\s+)?(?:typename\s+|class\s+|struct\s+|union\s+|enum\s+)?'
    r'(?:\w|'
    r'\s*<(?:<(?:<[^<>]*>|[^<>])*>|[^<>])*>|'
    r'::)+')
# A call-by-reference parameter ends with '& identifier'.
_RE_PATTERN_REF_PARAM = regex.compile(
    r'(' + _RE_PATTERN_TYPE + r'(?:\s*(?:\bconst\b|[*]))*\s*'
    r'&\s*' + _RE_PATTERN_IDENT + r')\s*(?:=[^,()]+)?[,)]')
# A call-by-const-reference parameter either ends with 'const& identifier'
# or looks like 'const type& identifier' when 'type' is atomic.
_RE_PATTERN_CONST_REF_PARAM = (
    r'(?:.*\s*\bconst\s*&\s*' + _RE_PATTERN_IDENT +
    r'|const\s+' + _RE_PATTERN_TYPE + r'\s*&\s*' + _RE_PATTERN_IDENT + r')')
# Stream types.
_RE_PATTERN_REF_STREAM_PARAM = (
    r'(?:.*stream\s*&\s*' + _RE_PATTERN_IDENT + r')')


def CheckLanguage(filename, clean_lines, linenum, is_header,
                  include_state, nesting_state, error):
  """Checks rules from the 'C++ language rules' section of cppguide.html.

  Some of these rules are hard to test (function overloading, using
  uint32 inappropriately), but we do the best we can.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    is_header: Whether file is header.
    include_state: An _IncludeState instance in which the headers are inserted.
    nesting_state: A NestingState instance which maintains information about
                   the current stack of nested blocks being parsed.
    error: The function to call with any errors found.
  """
  # If the line is empty or consists of entirely a comment, no need to
  # check it.
  line = clean_lines.elided[linenum]
  if not line:
    return

  match = _RE_PATTERN_INCLUDE.search(line)
  if match:
    CheckIncludeLine(filename, clean_lines, linenum, include_state, error)
    return

  # Reset include state across preprocessor directives.  This is meant
  # to silence warnings for conditional includes.
  match = Match(r'^\s*#\s*(if|ifdef|ifndef|elif|else|endif)\b', line)
  if match:
    include_state.ResetSection(match.group(1))


  # Perform other checks now that we are sure that this is not an include line
  CheckCasts(filename, clean_lines, linenum, error)
  CheckGlobalStatic(filename, clean_lines, linenum, error)
  CheckPrintf(filename, clean_lines, linenum, error)

  if is_header:
    # TODO(unknown): check that 1-arg constructors are explicit.
    #                How to tell it's a constructor?
    #                (handled in CheckForNonStandardConstructs for now)
    # TODO(unknown): check that classes declare or disable copy/assign
    #                (level 1 error)
    pass

  # Check if people are using the verboten C basic types.  The only exception
  # we regularly allow is "unsigned short port" for port.
  if Search(r'\bshort port\b', line):
    if not Search(r'\bunsigned short port\b', line):
      error(filename, linenum, 'runtime/int', 4,
            'Use "unsigned short" for ports, not "short"')
  else:
    match = Search(r'\b(short|long(?! +double)|long long)\b', line)
    if match:
      error(filename, linenum, 'runtime/int', 4,
            'Use int16/int64/etc, rather than the C type %s' % match.group(1))

  # Check if some verboten operator overloading is going on
  # TODO(unknown): catch out-of-line unary operator&:
  #   class X {};
  #   int operator&(const X& x) { return 42; }  // unary operator&
  # The trick is it's hard to tell apart from binary operator&:
  #   class Y { int operator&(const Y& x) { return 23; } }; // binary operator&
  if Search(r'\boperator\s*&\s*\(\s*\)', line):
    error(filename, linenum, 'runtime/operator', 4,
          'Unary operator& is dangerous.  Do not use it.')

  # Check for potential format string bugs like printf(foo).
  # We constrain the pattern not to pick things like DocidForPrintf(foo).
  # Not perfect but it can catch printf(foo.c_str()) and printf(foo->c_str())
  # TODO(unknown): Catch the following case. Need to change the calling
  # convention of the whole function to process multiple line to handle it.
  #   printf(
  #       boy_this_is_a_really_long_variable_that_cannot_fit_on_the_prev_line);
  printf_args = _GetTextInside(line, r'(?i)\b(string)?printf\s*\(')
  if printf_args:
    match = Match(r'([\w.\->()]+)$', printf_args)
    if match and match.group(1) != '__VA_ARGS__':
      function_name = regex.search(r'\b((?:string)?printf)\s*\(',
                                line, regex.I).group(1)
      error(filename, linenum, 'runtime/printf', 4,
            'Potential format string bug. Do %s("%%s", %s) instead.'
            % (function_name, match.group(1)))

  # Check for potential memset bugs like memset(buf, sizeof(buf), 0).
  match = Search(r'memset\s*\(([^,]*),\s*([^,]*),\s*0\s*\)', line)
  if match and not Match(r"^''|-?[0-9]+|0x[0-9A-Fa-f]$", match.group(2)):
    error(filename, linenum, 'runtime/memset', 4,
          'Did you mean "memset(%s, 0, %s)"?'
          % (match.group(1), match.group(2)))

  # Detect variable-length arrays.
  match = Match(r'\s*(.+::)?(\w+) [a-z]\w*\[(.+)];', line)
  if (match and match.group(2) != 'return' and match.group(2) != 'delete' and
      match.group(3).find(']') == -1):
    # Split the size using space and arithmetic operators as delimiters.
    # If any of the resulting tokens are not compile time constants then
    # report the error.
    tokens = regex.split(r'\s|\+|\-|\*|\/|<<|>>]', match.group(3))
    is_const = True
    skip_next = False
    for tok in tokens:
      if skip_next:
        skip_next = False
        continue

      if Search(r'sizeof\(.+\)', tok): continue
      if Search(r'arraysize\(\w+\)', tok): continue

      tok = tok.lstrip('(')
      tok = tok.rstrip(')')
      if not tok: continue
      if Match(r'\d+', tok): continue
      if Match(r'0[xX][0-9a-fA-F]+', tok): continue
      if Match(r'k[A-Z0-9]\w*', tok): continue
      if Match(r'(.+::)?k[A-Z0-9]\w*', tok): continue
      if Match(r'(.+::)?[A-Z][A-Z0-9_]*', tok): continue
      # A catch all for tricky sizeof cases, including 'sizeof expression',
      # 'sizeof(*type)', 'sizeof(const type)', 'sizeof(struct StructName)'
      # requires skipping the next token because we split on ' ' and '*'.
      if tok.startswith('sizeof'):
        skip_next = True
        continue
      is_const = False
      break
    if not is_const:
      error(filename, linenum, 'runtime/arrays', 1,
            'Do not use variable-length arrays.  Use an appropriately named '
            "('k' followed by CamelCase) compile-time constant for the size.")


def CheckGlobalStatic(filename, clean_lines, linenum, error):
  """Check for unsafe global or static objects.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    error: The function to call with any errors found.
  """
  line = clean_lines.elided[linenum]

  # Match two lines at a time to support multiline declarations
  if linenum + 1 < clean_lines.NumLines() and not Search(r'[;({]', line):
    line += clean_lines.elided[linenum + 1].strip()

  # Check for people declaring static/global STL strings at the top level.
  # This is dangerous because the C++ language does not guarantee that
  # globals with constructors are initialized before the first access, and
  # also because globals can be destroyed when some threads are still running.
  # TODO(unknown): Generalize this to also find static unique_ptr instances.
  # TODO(unknown): File bugs for clang-tidy to find these.
  match = Match(
      r'((?:|static +)(?:|const +))(?::*std::)?string( +const)? +'
      r'([a-zA-Z0-9_:]+)\b(.*)',
      line)

  if (Search(r'\b([A-Za-z0-9_]*_)\(\1\)', line) or
      Search(r'\b([A-Za-z0-9_]*_)\(CHECK_NOTNULL\(\1\)\)', line)):
    error(filename, linenum, 'runtime/init', 4,
          'You seem to be initializing a member variable with itself.')


def CheckPrintf(filename, clean_lines, linenum, error):
  """Check for printf related issues.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    error: The function to call with any errors found.
  """
  line = clean_lines.elided[linenum]

  # When snprintf is used, the second argument shouldn't be a literal.
  match = Search(r'snprintf\s*\(([^,]*),\s*([0-9]*)\s*,', line)
  if match and match.group(2) != '0':
    # If 2nd arg is zero, snprintf is used to calculate size.
    error(filename, linenum, 'runtime/printf', 3,
          'If you can, use sizeof(%s) instead of %s as the 2nd arg '
          'to snprintf.' % (match.group(1), match.group(2)))

  # Check if some verboten C functions are being used.
  if Search(r'\bsprintf\s*\(', line):
    error(filename, linenum, 'runtime/printf', 5,
          'Never use sprintf. Use snprintf instead.')
  match = Search(r'\b(strcpy|strcat)\s*\(', line)
  if match:
    error(filename, linenum, 'runtime/printf', 4,
          'Almost always, snprintf is better than %s' % match.group(1))


def CheckCasts(filename, clean_lines, linenum, error):
  """Various cast related checks.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    error: The function to call with any errors found.
  """
  line = clean_lines.elided[linenum]

  # Check to see if they're using an conversion function cast.
  # I just try to capture the most common basic types, though there are more.
  # Parameterless conversion functions, such as bool(), are allowed as they are
  # probably a member operator declaration or default constructor.
  match = Search(
      r'(\bnew\s+(?:const\s+)?|\S<\s*(?:const\s+)?)?\b'
      r'(int|float|double|bool|char|int32|uint32|int64|uint64)'
      r'(\([^)].*)', line)
  expecting_function = ExpectingFunctionArgs(clean_lines, linenum)
  if match and not expecting_function:
    matched_type = match.group(2)

    # matched_new_or_template is used to silence two false positives:
    # - New operators
    # - Template arguments with function types
    #
    # For template arguments, we match on types immediately following
    # an opening bracket without any spaces.  This is a fast way to
    # silence the common case where the function type is the first
    # template argument.  False negative with less-than comparison is
    # avoided because those operators are usually followed by a space.
    #
    #   function<double(double)>   // bracket + no space = false positive
    #   value < double(42)         // bracket + space = true positive
    matched_new_or_template = match.group(1)

    # Avoid arrays by looking for brackets that come after the closing
    # parenthesis.
    if Match(r'\([^()]+\)\s*\[', match.group(3)):
      return

    # Other things to ignore:
    # - Function pointers
    # - Casts to pointer types
    # - Placement new
    # - Alias declarations
    matched_funcptr = match.group(3)
    if (matched_new_or_template is None and
        not (matched_funcptr and
             (Match(r'\((?:[^() ]+::\s*\*\s*)?[^() ]+\)\s*\(',
                    matched_funcptr) or
              matched_funcptr.startswith('(*)'))) and
        not Match(r'\s*using\s+\S+\s*=\s*' + matched_type, line) and
        not Search(r'new\(\S+\)\s*' + matched_type, line)):
      error(filename, linenum, 'readability/casting', 4,
            'Using deprecated casting style.  '
            'Use static_cast<%s>(...) instead' %
            matched_type)

  if not expecting_function:
    # This doesn't check for short, long, or long long integer casts because
    # they are disallowed by other lint rules.
    CheckCStyleCast(filename, clean_lines, linenum, 'static_cast',
                    r'\((unsigned|(unsigned )?(char|int)|float|double|bool|'
                    r'u?int(8|16|32|64)(_t)?)\)', error)

  # This doesn't catch all cases. Consider (const char * const)"hello".
  #
  # (char *) "foo" should always be a const_cast (reinterpret_cast won't
  # compile).
  if CheckCStyleCast(filename, clean_lines, linenum, 'const_cast',
                     r'\((char\s?\*+\s?)\)\s*"', error):
    pass
  else:
    # Check pointer casts for other than string constants
    CheckCStyleCast(filename, clean_lines, linenum, 'reinterpret_cast',
                    r'\(((const )?\w+\s?\*+\s?(const)?)\)', error)

  # In addition, we look for people taking the address of a cast.  This
  # is dangerous -- casts can assign to temporaries, so the pointer doesn't
  # point where you think.
  #
  # Some non-identifier character is required before the '&' for the
  # expression to be recognized as a cast.  These are casts:
  #   expression = &static_cast<int*>(temporary());
  #   function(&(int*)(temporary()));
  #
  # This is not a cast:
  #   reference_type&(int* function_param);
  match = Search(
      r'(?:[^\w]&\(([^)*][^)]*)\)[\w(])|'
      r'(?:[^\w]&(static|dynamic|down|reinterpret)_cast\b)', line)
  if match:
    # Try a better error message when the & is bound to something
    # dereferenced by the casted pointer, as opposed to the casted
    # pointer itself.
    parenthesis_error = False
    match = Match(r'^(.*&(?:static|dynamic|down|reinterpret)_cast\b)<', line)
    if match:
      _, y1, x1 = CloseExpression(clean_lines, linenum, len(match.group(1)))
      if x1 >= 0 and clean_lines.elided[y1][x1] == '(':
        _, y2, x2 = CloseExpression(clean_lines, y1, x1)
        if x2 >= 0:
          extended_line = clean_lines.elided[y2][x2:]
          if y2 < clean_lines.NumLines() - 1:
            extended_line += clean_lines.elided[y2 + 1]
          if Match(r'\s*(?:->|\[)', extended_line):
            parenthesis_error = True

    if parenthesis_error:
      error(filename, linenum, 'readability/casting', 4,
            ('Are you taking an address of something dereferenced '
             'from a cast?  Wrapping the dereferenced expression in '
             'parentheses will make the binding more obvious'))
    else:
      error(filename, linenum, 'runtime/casting', 4,
            ('Are you taking an address of a cast?  '
             'This is dangerous: could be a temp var.  '
             'Take the address before doing the cast, rather than after'))


def CheckCStyleCast(filename, clean_lines, linenum, cast_type, pattern, error):
  """Checks for a C-style cast by looking for the pattern.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    cast_type: The string for the C++ cast to recommend.  This is either
      reinterpret_cast, static_cast, or const_cast, depending.
    pattern: The regular expression used to find C-style casts.
    error: The function to call with any errors found.

  Returns:
    True if an error was emitted.
    False otherwise.
  """
  line = clean_lines.elided[linenum]
  match = Search(pattern, line)
  if not match:
    return False

  # Exclude lines with keywords that tend to look like casts
  context = line[0:match.start(1) - 1]
  if Match(r'.*\b(?:sizeof|alignof|alignas|[_A-Z][_A-Z0-9]*)\s*$', context):
    return False

  # Try expanding current context to see if we one level of
  # parentheses inside a macro.
  if linenum > 0:
    for i in range(linenum - 1, max(0, linenum - 5), -1):
      context = clean_lines.elided[i] + context
  if Match(r'.*\b[_A-Z][_A-Z0-9]*\s*\((?:\([^()]*\)|[^()])*$', context):
    return False

  # operator++(int) and operator--(int)
  if context.endswith(' operator++') or context.endswith(' operator--'):
    return False

  # A single unnamed argument for a function tends to look like old style cast.
  # If we see those, don't issue warnings for deprecated casts.
  remainder = line[match.end(0):]
  if Match(r'^\s*(?:;|const\b|throw\b|noexcept\b|final\b|override\b|[=>{),]|->)',
           remainder):
    return False

  # At this point, all that should be left is actual casts.
  error(filename, linenum, 'readability/casting', 4,
        'Using C-style cast.  Use %s<%s>(...) instead' %
        (cast_type, match.group(1)))

  return True


def ExpectingFunctionArgs(clean_lines, linenum):
  """Checks whether where function type arguments are expected.

  Args:
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.

  Returns:
    True if the line at 'linenum' is inside something that expects arguments
    of function types.
  """
  line = clean_lines.elided[linenum]
  return (Match(r'^\s*MOCK_(CONST_)?METHOD\d+(_T)?\(', line) or
          (linenum >= 2 and
           (Match(r'^\s*MOCK_(?:CONST_)?METHOD\d+(?:_T)?\((?:\S+,)?\s*$',
                  clean_lines.elided[linenum - 1]) or
            Match(r'^\s*MOCK_(?:CONST_)?METHOD\d+(?:_T)?\(\s*$',
                  clean_lines.elided[linenum - 2]) or
            Search(r'\bstd::m?function\s*\<\s*$',
                   clean_lines.elided[linenum - 1]))))


_HEADERS_CONTAINING_TEMPLATES = (
    ('<deque>', ('deque',)),
    ('<functional>', ('function', 'unary_function', 'binary_function',
                      'plus', 'minus', 'multiplies', 'divides', 'modulus',
                      'negate',
                      'equal_to', 'not_equal_to', 'greater', 'less',
                      'greater_equal', 'less_equal',
                      'logical_and', 'logical_or', 'logical_not',
                      'unary_negate', 'not1', 'binary_negate', 'not2',
                      'bind1st', 'bind2nd',
                      'pointer_to_unary_function',
                      'pointer_to_binary_function',
                      'ptr_fun',
                      'mem_fun_t', 'mem_fun', 'mem_fun1_t', 'mem_fun1_ref_t',
                      'mem_fun_ref_t',
                      'const_mem_fun_t', 'const_mem_fun1_t',
                      'const_mem_fun_ref_t', 'const_mem_fun1_ref_t',
                      'mem_fun_ref',
                     )),
    ('<limits>', ('numeric_limits',)),
    ('<list>', ('list',)),
    ('<map>', ('map', 'multimap',)),
    ('<memory>', ('allocator', 'make_shared', 'make_unique', 'shared_ptr',
                  'unique_ptr', 'weak_ptr')),
    ('<queue>', ('queue', 'priority_queue',)),
    ('<set>', ('set', 'multiset',)),
    ('<stack>', ('stack',)),
    ('<string>', ('char_traits', 'basic_string',)),
    ('<tuple>', ('tuple',)),
    ('<unordered_map>', ('unordered_map', 'unordered_multimap')),
    ('<unordered_set>', ('unordered_set', 'unordered_multiset')),
    ('<utility>', ('pair',)),
    ('<vector>', ('vector',)),

    # gcc extensions.
    # Note: std::hash is their hash, ::hash is our hash
    ('<hash_map>', ('hash_map', 'hash_multimap',)),
    ('<hash_set>', ('hash_set', 'hash_multiset',)),
    ('<slist>', ('slist',)),
    )

_HEADERS_MAYBE_TEMPLATES = (
    ('<algorithm>', ('copy', 'max', 'min', 'min_element', 'sort',
                     'transform',
                    )),
    ('<utility>', ('forward', 'make_pair', 'move', 'swap')),
    )

_RE_PATTERN_STRING = regex.compile(r'\bstring\b')

_re_pattern_headers_maybe_templates = []
for _header, _templates in _HEADERS_MAYBE_TEMPLATES:
  for _template in _templates:
    # Match max<type>(..., ...), max(..., ...), but not foo->max, foo.max or
    # type::max().
    _re_pattern_headers_maybe_templates.append(
        (regex.compile(r'[^>.]\b' + _template + r'(<.*?>)?\([^\)]'),
            _template,
            _header))

# Other scripts may reach in and modify this pattern.
_re_pattern_templates = []
for _header, _templates in _HEADERS_CONTAINING_TEMPLATES:
  for _template in _templates:
    _re_pattern_templates.append(
        (regex.compile(r'(\<|\b)' + _template + r'\s*\<'),
         _template + '<>',
         _header))


def FilesBelongToSameModule(filename_cc, filename_h):
  """Check if these two filenames belong to the same module.

  The concept of a 'module' here is a as follows:
  foo.h, foo-inl.h, foo.cc, foo_test.cc and foo_unittest.cc belong to the
  same 'module' if they are in the same directory.
  some/path/public/xyzzy and some/path/internal/xyzzy are also considered
  to belong to the same module here.

  If the filename_cc contains a longer path than the filename_h, for example,
  '/absolute/path/to/base/sysinfo.cc', and this file would include
  'base/sysinfo.h', this function also produces the prefix needed to open the
  header. This is used by the caller of this function to more robustly open the
  header file. We don't have access to the real include paths in this context,
  so we need this guesswork here.

  Known bugs: tools/base/bar.cc and base/bar.h belong to the same module
  according to this implementation. Because of this, this function gives
  some false positives. This should be sufficiently rare in practice.

  Args:
    filename_cc: is the path for the source (e.g. .cc) file
    filename_h: is the path for the header path

  Returns:
    Tuple with a bool and a string:
    bool: True if filename_cc and filename_h belong to the same module.
    string: the additional prefix needed to open the header file.
  """
  fileinfo_cc = FileInfo(filename_cc)
  if not IsSourceFile(filename_cc):
    return (False, '')

  fileinfo_h = FileInfo(filename_h)
  if not IsHeaderFile(filename_h):
    return (False, '')

  filename_cc = filename_cc[:-(len(fileinfo_cc.Extension()))]

  filename_cc = filename_cc.replace('/public/', '/')
  filename_cc = filename_cc.replace('/internal/', '/')

  filename_h = filename_h[:-(len(fileinfo_h.Extension()))]
  if filename_h.endswith('-inl'):
    filename_h = filename_h[:-len('-inl')]
  filename_h = filename_h.replace('/public/', '/')
  filename_h = filename_h.replace('/internal/', '/')

  files_belong_to_same_module = filename_cc.endswith(filename_h)
  common_path = ''
  if files_belong_to_same_module:
    common_path = filename_cc[:-len(filename_h)]
  return files_belong_to_same_module, common_path


def UpdateIncludeState(filename, include_dict, io=codecs):
  """Fill up the include_dict with new includes found from the file.

  Args:
    filename: the name of the header to read.
    include_dict: a dictionary in which the headers are inserted.
    io: The io factory to use to read the file. Provided for testability.

  Returns:
    True if a header was successfully added. False otherwise.
  """
  headerfile = None
  try:
    headerfile = io.open(filename, 'r', 'utf8', 'replace')
  except IOError:
    return False
  linenum = 0
  for line in headerfile:
    linenum += 1
    clean_line = CleanseComments(line)
    match = _RE_PATTERN_INCLUDE.search(clean_line)
    if match:
      include = match.group(2)
      include_dict.setdefault(include, linenum)
  return True


def CheckForIncludeWhatYouUse(filename, clean_lines, include_state, error,
                              io=codecs):
  """Reports for missing stl includes.

  This function will output warnings to make sure you are including the headers
  necessary for the stl containers and functions that you use. We only give one
  reason to include a header. For example, if you use both equal_to<> and
  less<> in a .h file, only one (the latter in the file) of these will be
  reported as a reason to include the <functional>.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    include_state: An _IncludeState instance.
    error: The function to call with any errors found.
    io: The IO factory to use to read the header file. Provided for unittest
        injection.
  """
  required = {}  # A map of header name to linenumber and the template entity.
                 # Example of required: { '<functional>': (1219, 'less<>') }

  for linenum in range(clean_lines.NumLines()):
    line = clean_lines.elided[linenum]
    if not line or line[0] == '#':
      continue

    # String is special -- it is a non-templatized type in STL.
    matched = _RE_PATTERN_STRING.search(line)
    if matched:
      # Don't warn about strings in non-STL namespaces:
      # (We check only the first match per line; good enough.)
      prefix = line[:matched.start()]
      if prefix.endswith('std::') or not prefix.endswith('::'):
        required['<string>'] = (linenum, 'string')

    for pattern, template, header in _re_pattern_headers_maybe_templates:
      if pattern.search(line):
        required[header] = (linenum, template)

    # The following function is just a speed up, no semantics are changed.
    if not '<' in line:  # Reduces the cpu time usage by skipping lines.
      continue

    for pattern, template, header in _re_pattern_templates:
      matched = pattern.search(line)
      if matched:
        # Don't warn about IWYU in non-STL namespaces:
        # (We check only the first match per line; good enough.)
        prefix = line[:matched.start()]
        if prefix.endswith('std::') or not prefix.endswith('::'):
          required[header] = (linenum, template)

  # The policy is that if you #include something in foo.h you don't need to
  # include it again in foo.cc. Here, we will look at possible includes.
  # Let's flatten the include_state include_list and copy it into a dictionary.
  include_dict = dict([item for sublist in include_state.include_list
                       for item in sublist])

  # Did we find the header for this file (if any) and successfully load it?
  header_found = False

  # Use the absolute path so that matching works properly.
  abs_filename = FileInfo(filename).FullName()

  # include_dict is modified during iteration, so we iterate over a copy of
  # the keys.
  header_keys = list(include_dict.keys())
  for header in header_keys:
    (same_module, common_path) = FilesBelongToSameModule(abs_filename, header)
    fullpath = common_path + header
    if same_module and UpdateIncludeState(fullpath, include_dict, io):
      header_found = True

  # If we can't find the header file for a .cc, assume it's because we don't
  # know where to look. In that case we'll give up as we're not sure they
  # didn't include it in the .h file.
  # TODO(unknown): Do a better job of finding .h files so we are confident that
  # not having the .h file means there isn't one.
  if not header_found:
    if IsSourceFile(filename):
      return

  # All the lines have been processed, report the errors found.
  for required_header_unstripped in sorted(required, key=required.__getitem__):
    template = required[required_header_unstripped][1]
    if required_header_unstripped.strip('<>"') not in include_dict:
      error(filename, required[required_header_unstripped][0],
            'build/include_what_you_use', 4,
            'Add #include ' + required_header_unstripped + ' for ' + template)


_RE_PATTERN_EXPLICIT_MAKEPAIR = regex.compile(r'\bmake_pair\s*<')


def CheckMakePairUsesDeduction(filename, clean_lines, linenum, error):
  """Check that make_pair's template arguments are deduced.

  G++ 4.6 in C++11 mode fails badly if make_pair's template arguments are
  specified explicitly, and such use isn't intended in any case.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    error: The function to call with any errors found.
  """
  line = clean_lines.elided[linenum]
  match = _RE_PATTERN_EXPLICIT_MAKEPAIR.search(line)
  if match:
    error(filename, linenum, 'build/explicit_make_pair',
          4,  # 4 = high confidence
          'For C++11-compatibility, omit template arguments from make_pair'
          ' OR use pair directly OR if appropriate, construct a pair directly')


def CheckRedundantVirtual(filename, clean_lines, linenum, error):
  """Check if line contains a redundant "virtual" function-specifier.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    error: The function to call with any errors found.
  """
  # Look for "virtual" on current line.
  line = clean_lines.elided[linenum]
  virtual = Match(r'^(.*)(\bvirtual\b)(.*)$', line)
  if not virtual: return

  # Ignore "virtual" keywords that are near access-specifiers.  These
  # are only used in class base-specifier and do not apply to member
  # functions.
  if (Search(r'\b(public|protected|private)\s+$', virtual.group(1)) or
      Match(r'^\s+(public|protected|private)\b', virtual.group(3))):
    return

  # Ignore the "virtual" keyword from virtual base classes.  Usually
  # there is a column on the same line in these cases (virtual base
  # classes are rare in google3 because multiple inheritance is rare).
  if Match(r'^.*[^:]:[^:].*$', line): return

  # Look for the next opening parenthesis.  This is the start of the
  # parameter list (possibly on the next line shortly after virtual).
  # TODO(unknown): doesn't work if there are virtual functions with
  # decltype() or other things that use parentheses, but csearch suggests
  # that this is rare.
  end_col = -1
  end_line = -1
  start_col = len(virtual.group(2))
  for start_line in range(linenum, min(linenum + 3, clean_lines.NumLines())):
    line = clean_lines.elided[start_line][start_col:]
    parameter_list = Match(r'^([^(]*)\(', line)
    if parameter_list:
      # Match parentheses to find the end of the parameter list
      (_, end_line, end_col) = CloseExpression(
          clean_lines, start_line, start_col + len(parameter_list.group(1)))
      break
    start_col = 0

  if end_col < 0:
    return  # Couldn't find end of parameter list, give up

  # Look for "override" or "final" after the parameter list
  # (possibly on the next few lines).
  for i in range(end_line, min(end_line + 3, clean_lines.NumLines())):
    line = clean_lines.elided[i][end_col:]
    match = Search(r'\b(override|final)\b', line)
    if match:
      error(filename, linenum, 'readability/inheritance', 4,
            ('"virtual" is redundant since function is '
             'already declared as "%s"' % match.group(1)))

    # Set end_col to check whole lines after we are done with the
    # first line.
    end_col = 0
    if Search(r'[^\w]\s*$', line):
      break


def CheckRedundantOverrideOrFinal(filename, clean_lines, linenum, error):
  """Check if line contains a redundant "override" or "final" virt-specifier.

  Args:
    filename: The name of the current file.
    clean_lines: A CleansedLines instance containing the file.
    linenum: The number of the line to check.
    error: The function to call with any errors found.
  """
  # Look for closing parenthesis nearby.  We need one to confirm where
  # the declarator ends and where the virt-specifier starts to avoid
  # false positives.
  line = clean_lines.elided[linenum]
  declarator_end = line.rfind(')')
  if declarator_end >= 0:
    fragment = line[declarator_end:]
  else:
    if linenum > 1 and clean_lines.elided[linenum - 1].rfind(')') >= 0:
      fragment = line
    else:
      return

  # Check that at most one of "override" or "final" is present, not both
  if Search(r'\boverride\b', fragment) and Search(r'\bfinal\b', fragment):
    error(filename, linenum, 'readability/inheritance', 4,
          ('"override" is redundant since function is '
           'already declared as "final"'))


# Returns true if we are at a new block, and it is directly
# inside of a namespace.
def IsBlockInNameSpace(nesting_state, is_forward_declaration):
  """Checks that the new block is directly in a namespace.

  Args:
    nesting_state: The _NestingState object that contains info about our state.
    is_forward_declaration: If the class is a forward declared class.
  Returns:
    Whether or not the new block is directly in a namespace.
  """
  if is_forward_declaration:
    return len(nesting_state.stack) >= 1 and (
      isinstance(nesting_state.stack[-1], _NamespaceInfo))


  return (len(nesting_state.stack) > 1 and
          nesting_state.stack[-1].check_namespace_indentation and
          isinstance(nesting_state.stack[-2], _NamespaceInfo))


def ProcessLine(filename, is_header, clean_lines, line,
                include_state, function_state, nesting_state, error):
  """Processes a single line in the file.

  Args:
    filename: Filename of the file that is being processed.
    is_header: Whether file is header.
    clean_lines: An array of strings, each representing a line of the file,
                 with comments stripped.
    line: Number of line being processed.
    include_state: An _IncludeState instance in which the headers are inserted.
    function_state: A _FunctionState instance which counts function lines, etc.
    nesting_state: A NestingState instance which maintains information about
                   the current stack of nested blocks being parsed.
    error: A callable to which errors are reported, which takes 4 arguments:
           filename, line number, error level, and message
  """
  raw_lines = clean_lines.raw_lines
  ParseNolintSuppressions(filename, raw_lines[line], line, error)
  nesting_state.Update(filename, clean_lines, line, error)
  if nesting_state.InAsmBlock(): return
  CheckForFunctionLengths(filename, clean_lines, line, function_state, error)
  CheckForMultilineCommentsAndStrings(filename, clean_lines, line, error)
  CheckStyle(filename, clean_lines, line, is_header, nesting_state, error)
  CheckLanguage(filename, clean_lines, line, is_header, include_state,
                nesting_state, error)
  CheckForNonStandardConstructs(filename, clean_lines, line,
                                nesting_state, error)
  CheckInvalidIncrement(filename, clean_lines, line, error)
  CheckMakePairUsesDeduction(filename, clean_lines, line, error)
  CheckRedundantVirtual(filename, clean_lines, line, error)
  CheckRedundantOverrideOrFinal(filename, clean_lines, line, error)


def ProcessFileData(filename, is_header, lines, error):
  """Performs lint checks and reports any errors to the given error function.

  Args:
    filename: Filename of the file that is being processed.
    is_header: Whether file is header.
    lines: An array of strings, each representing a line of the file, with the
           last element being empty if the file is terminated with a newline.
    error: A callable to which errors are reported, which takes 4 arguments:
           filename, line number, error level, and message
  """
  lines = (['// marker so line numbers and indices both start at 1'] + lines +
           ['// marker so line numbers end in a known way'])

  include_state = _IncludeState()
  function_state = _FunctionState()
  nesting_state = NestingState()

  ResetNolintSuppressions()

  ProcessGlobalSuppresions(lines)
  RemoveMultiLineComments(filename, lines, error)
  clean_lines = CleansedLines(lines)

  for line in range(clean_lines.NumLines()):
    ProcessLine(filename, is_header, clean_lines, line,
                include_state, function_state, nesting_state, error)

  CheckForIncludeWhatYouUse(filename, clean_lines, include_state, error)

  # We check here rather than inside ProcessLine so that we see raw
  # lines rather than "cleaned" lines.
  CheckForBadCharacters(filename, lines, error)


def ProcessFile(filename):
  """Does google-lint on a single file.

  Args:
    filename: The name of the file to parse.
  """

  # Note that
  # we are not opening the file with universal newline support
  # (which codecs doesn't support anyway), so the resulting lines do
  # contain trailing '\r' characters if we are reading a file that
  # has CRLF endings.
  # If after the split a trailing '\r' is present, it is removed
  # below.
  lines = codecs.open(filename, 'r', 'utf8', 'replace').read().split('\n')

  # Remove trailing '\r'.
  # The -1 accounts for the extra trailing blank line we get from split()
  for linenum in range(len(lines) - 1):
    if lines[linenum].endswith('\r'):
      lines[linenum] = lines[linenum].rstrip('\r')

  is_header = IsHeaderFile(filename)

  ProcessFileData(filename, is_header, lines, Error)


def PrintUsage(message):
  """Prints a brief usage string and exits, optionally with an error message.

  Args:
    message: The optional error message.
  """
  sys.stderr.write(_USAGE)

  if message:
    sys.exit('\nFATAL ERROR: ' + message)
  else:
    sys.exit(0)


def ParseArguments(args):
  """Parses the command line arguments.

  This may set the output format and verbosity level as side-effects.

  Args:
    args: The command line arguments:

  Returns:
    The list of filenames to lint.
  """
  try:
    (opts, filenames) = getopt.getopt(args, '', ['help',
                                                 'srcs=',
                                                 'headers='])
  except getopt.GetoptError:
    PrintUsage('Invalid arguments.')

  for (opt, val) in opts:
    if opt == '--help':
      PrintUsage(None)
    elif opt == '--srcs':
      global _source_regex
      try:
        _source_regex = regex.compile(val)
      except ValueError:
          PrintUsage('Extensions must be comma seperated list.')
    elif opt == '--headers':
      global _header_regex
      try:
          _header_regex = regex.compile(val)
      except ValueError:
        PrintUsage('Extensions must be comma seperated list.')

  if not filenames:
    PrintUsage('No files were specified.')

  return filenames


def main():
  filenames = ParseArguments(sys.argv[1:])
  backup_err = sys.stderr
  try:
    # Change stderr to write with replacement characters so we don't die
    # if we try to print something containing non-ASCII characters.
    sys.stderr = codecs.StreamReader(sys.stderr, 'replace')

    _cpplint_state.ResetErrorCounts()
    for filename in filenames:
      ProcessFile(filename)

  finally:
    sys.stderr = backup_err

  sys.exit(_cpplint_state.error_count > 0)


if __name__ == '__main__':
  main()
