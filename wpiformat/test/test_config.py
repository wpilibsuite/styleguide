from pathlib import Path

from wpiformat.config import Config


def test_config():
    config_file = Config(Path.cwd(), Path(".wpiformat"))
    assert config_file.is_modifiable_file(
        Path("./wpiformat/javaguidelink.png").resolve()
    )
    assert config_file.is_generated_file(
        Path("./wpiformat/wpiformat/cpplint.py").resolve()
    )

    assert not config_file.is_generated_file(
        Path("./wpiformat/diff_cpplint.py").resolve()
    )
    assert not config_file.is_generated_file(
        Path("./wpiformat/update_cpplint.py").resolve()
    )
    assert not config_file.is_modifiable_file(Path("./wpiformat/license.txt").resolve())
