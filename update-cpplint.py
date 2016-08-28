#!/usr/bin/env python3

"""Downloads the latest cpplint.py and edits it for use by lint.py.

Dependencies:
    python-patch
"""

import urllib.request
import shutil
import subprocess
import sys

import patch

def main():
    print("Downloading cpplint.py...", end = "")
    sys.stdout.flush()
    url = "https://raw.githubusercontent.com/google/styleguide/gh-pages/cpplint/cpplint.py"
    with urllib.request.urlopen(url) as response, \
            open("cpplint.py", "wb") as out:
        data = response.read()
        out.write(data)
    print(" done")

    print("Converting cpplint.py from Python 2 to Python 3...", end = "")
    sys.stdout.flush()
    if subprocess.call(["2to3", "-f", "all", "-f", "buffer", "-f", "idioms",
                        "-f", "set_literal", "-f", "ws_comma", "-nw",
                        "cpplint.py"], stdout = subprocess.DEVNULL,
                        stderr = subprocess.DEVNULL) == -1:
        print("Error: 2to3 not found in PATH")
        sys.exit(1)
    print(" done")

    print("Applying custom patches...", end = "")
    sys.stdout.flush()
    patchSet = patch.fromfile("cpplint.patch")
    patchSet.apply()
    print(" done")

if __name__ == "__main__":
    main()
