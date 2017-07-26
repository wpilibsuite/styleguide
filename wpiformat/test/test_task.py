import os

import wpiformat.task as task


def test_task():
    assert task.is_generated_file("." + os.sep + "wpiformat" + os.sep +
                                  "wpiformat" + os.sep + "cpplint.py")
    assert task.is_modifiable_file("." + os.sep + "wpiformat" + os.sep +
                                   "javaguidelink.png")

    assert not task.is_generated_file("." + os.sep + "wpiformat" + os.sep +
                                      "diff_cpplint.py")
    assert not task.is_generated_file("." + os.sep + "wpiformat" + os.sep +
                                      "update_cpplint.py")
    assert not task.is_modifiable_file("." + os.sep + "wpiformat" + os.sep +
                                       "license.txt")
