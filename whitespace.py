"""This task removes trailing whitespace from the file."""

import os

from task import Task

class Whitespace(Task):
    def run(self, name):
        file_changed = False
        with open(name, "r") as file, open(name + ".tmp", "w") as temp:
            for line in file:
                processed_line = line[0:len(line) - 1].rstrip() + "\n"
                if not file_changed and len(line) != len(processed_line):
                    file_changed = True
                temp.write(processed_line)

        # Replace old file if it was changed
        if file_changed:
            os.remove(name)
            os.rename(name + ".tmp", name)
        else:
            os.remove(name + ".tmp")
