"""This task runs gersemi on CMake files."""

import subprocess
import sys

from wpiformat.task import Task


class CMakeFormat(Task):
    @staticmethod
    def should_process_file(config_file, name):
        return name.endswith("CMakeLists.txt") or name.endswith(".cmake")

    @staticmethod
    def run_batch(config_file, names):
        try:
            args = [
                sys.executable,
                "-m",
                "gersemi",
                "-i",
                "apriltag",
                "cameraserver",
                "cmake/modules",
                "cmake/scripts",
                "cscore",
                "datalogtool",
                "fieldImages",
                "hal",
                "imgui",
                "ntcore",
                "outlineviewer",
                "roborioteamnumbersetter",
                "romiVendordep",
                "simulation",
                "sysid",
                "wpigui",
                "wpilibc",
                "wpilibcExamples",
                "wpilibj",
                "wpilibNewCommands",
                "wpimath",
                "wpinet",
                "wpiunits",
                "wpiutil",
                "xrpVendordep",
                "CMakeLists.txt",
            ]
            returncode = subprocess.run(args + names).returncode
        except FileNotFoundError:
            print("Error: gersemi not found in PATH. Is it installed?", file=sys.stderr)
            return False
        return True
