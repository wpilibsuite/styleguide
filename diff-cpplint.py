#!/usr/bin/env python3

"""Downloads the latest cpplint.py and generates a diff between it and the local
version.
"""

import urllib.request
import subprocess
import os
import re
import sys

# Check that the current directory is part of a Git repository
def in_git_repo(directory):
    ret = subprocess.run(["git", "rev-parse"], stderr = subprocess.DEVNULL)
    return ret.returncode == 0

def main():
    if not in_git_repo("."):
        print("Error: not invoked within a Git repository", file = sys.stderr)
        sys.exit(1)

    print("Downloading cpplint.py...", end = "")
    sys.stdout.flush()
    url = "https://raw.githubusercontent.com/theandrewdavis/cpplint/master/cpplint.py"
    with urllib.request.urlopen(url) as response, \
            open("cpplint.py.master", "wb") as out:
        data = response.read()
        out.write(data)
    print(" done")

    print("Generating patch...", end = "")
    sys.stdout.flush()

    # Generate diff
    proc = subprocess.Popen(["git", "diff", "--no-index", "cpplint.py.master",
                             "cpplint.py"], stdout = subprocess.PIPE)
    diff, err = proc.communicate()

    # Write diff to file
    with open("cpplint.patch", "w") as diff_file:
        index_regex = re.compile("index [0-9a-f]{7}\.\.[0-9a-f]{7}")
        for line in diff.decode("ascii").splitlines():
            # Skip "index" line
            if not index_regex.search(line):
                line = line.replace("cpplint.py.master", "cpplint.py")
                diff_file.write(line + "\n")

    # Remove "from" file
    os.remove("cpplint.py.master")
    print(" done")

if __name__ == "__main__":
    main()
