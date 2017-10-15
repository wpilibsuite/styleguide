#!/usr/bin/env python

from datetime import date
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import exists
from os.path import join
from os.path import splitext
from setuptools import find_packages
from setuptools import setup
import subprocess
import sys

setup_dir = dirname(__file__)
git_dir = join(setup_dir, "../.git")
base_package = "wpiformat"
version_file = join(setup_dir, base_package, "version.py")

# Automatically generate a version.py based on the git version
if exists(git_dir):
    proc = subprocess.Popen(
        [
            "git",
            "rev-list",
            "--count",
            # Includes previous year's commits in case one was merged after the
            # year incremented. Otherwise, the version wouldn't increment.
            "--after=\"master@{" + str(date.today().year - 1) + "-01-01}\"",
            "master"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    commit_count, err = proc.communicate()
    # If there is no master branch, the commit count defaults to 0
    if err:
        commit_count = 0

    # Version number: <year>.<# commits on master>
    version = \
        str(date.today().year) + "." + commit_count.decode("utf-8").strip()

    # Create the version.py file
    with open(version_file, 'w') as fp:
        fp.write("# Autogenerated by setup.py\n__version__ = \"{0}\""
                 .format(version))

if exists(version_file):
    with open(version_file, "r") as fp:
        exec(fp.read(), globals())
else:
    __version__ = "master"

with open(join(setup_dir, "README.rst"), "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="wpiformat",
    version=__version__,
    description=
    "Linters and formatters for ensuring WPILib\'s source code conforms to its style guide",
    long_description=long_description,
    author="WPILib",
    maintainer="Tyler Veness",
    maintainer_email="calcmogul@gmail.com",
    url="https://github.com/wpilibsuite/styleguide",
    keywords="frc first robotics wpilib",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    install_requires=["yapf"],
    license="BSD License",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers", "Intended Audience :: Education",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent", "Topic :: Scientific/Engineering",
        "Programming Language :: Python :: 3"
    ],
    entry_points={
        "console_scripts": ["wpiformat = wpiformat:main"]
    })
