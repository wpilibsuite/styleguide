import os
import tempfile


class OpenTemporaryDirectory():

    def __init__(self):
        self.prev_dir = os.getcwd()

    def __enter__(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        os.chdir(self.temp_dir.name)
        return self.temp_dir

    def __exit__(self, type, value, traceback):
        os.chdir(self.prev_dir)
