import subprocess
from pathlib import Path

from wpiformat.config import Config

from .test_tasktest import OpenTemporaryDirectory


def test_config():
    with OpenTemporaryDirectory():
        subprocess.run(["git", "init", "-q"])
        Path(".wpiformat").write_text(
            r"""generatedFileExclude {
  /cpplint\.py$
}

modifiableFileExclude {
  \.png$
}
"""
        )

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
        assert not config_file.is_modifiable_file(
            Path("./wpiformat/license.txt").resolve()
        )
