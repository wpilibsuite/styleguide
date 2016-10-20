#!/usr/bin/env python3
"""Downloads the latest cpplint.py and edits it for use by lint.py.

Dependencies:
    python-patch
"""

import urllib.request
import sys

import patch


def main():
    print("Downloading cpplint.py...", end="")
    sys.stdout.flush()
    url = "https://raw.githubusercontent.com/theandrewdavis/cpplint/master/cpplint.py"
    with urllib.request.urlopen(url) as response, \
            open("wpiformat" + os.sep + "src" + os.sep + "cpplint.py", "wb") as out:
        data = response.read()
        out.write(data)
    print(" done")

    print("Applying custom patches...", end="")
    sys.stdout.flush()
    patch_set = patch.fromfile("wpiformat" + os.sep + "src" + os.sep +
                               "cpplint.patch")
    patch_set.apply()
    print(" done")


if __name__ == "__main__":
    main()
