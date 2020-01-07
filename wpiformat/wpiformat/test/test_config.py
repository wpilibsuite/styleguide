import os

from wpiformat.config import Config


def test_config():
    config_file = Config(os.path.abspath(os.getcwd()), ".styleguide")
    assert config_file.is_modifiable_file("." + os.sep + "wpiformat" + os.sep +
                                          "javaguidelink.png")
    assert config_file.is_generated_file("." + os.sep + "wpiformat" + os.sep +
                                         "wpiformat" + os.sep + "cpplint.py")

    assert not config_file.is_generated_file("." + os.sep + "wpiformat" +
                                             os.sep + "diff_cpplint.py")
    assert not config_file.is_generated_file("." + os.sep + "wpiformat" +
                                             os.sep + "update_cpplint.py")
    assert not config_file.is_modifiable_file("." + os.sep + "wpiformat" +
                                              os.sep + "license.txt")
