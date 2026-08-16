import sys
from typing import ClassVar

import pytest

import wpiformat


class SynchronousPool:
    callbacks: ClassVar[list[str]] = []

    def __init__(self, _jobs, initializer, init_args):
        initializer(*init_args)

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        pass

    def map(self, callback, iterable):
        self.callbacks.append(callback.__name__)
        return [callback(item) for item in iterable]


def test_main_continues_after_non_utf8_file(monkeypatch, tmp_path, capsys):
    invalid_filename = tmp_path / "foo"
    invalid_filename.write_bytes(b"\xff")

    warning_filename = tmp_path / "warning.cpp"
    warning_filename.write_text("using namespace std;\n")
    (tmp_path / ".wpiformat").write_text(
        "licenseUpdateExclude {\n  warning\\.cpp$\n}\n"
    )
    (tmp_path / ".clang-format").write_text("BasedOnStyle: Google\n")

    SynchronousPool.callbacks = []
    monkeypatch.setattr(wpiformat.mp, "Pool", SynchronousPool)
    monkeypatch.setattr(wpiformat.Task, "get_repo_root", lambda: tmp_path)
    monkeypatch.setattr(wpiformat, "filter_for_unignored_files", lambda files: files)
    monkeypatch.setattr(
        wpiformat.subprocess, "check_output", lambda *args, **kwargs: ""
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wpiformat",
            "-j",
            "1",
            "-default-branch",
            "main",
            "-f",
            str(invalid_filename),
            str(warning_filename),
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        wpiformat.main()

    assert exc_info.value.code == 1

    output = capsys.readouterr().out
    invalid_file_error = f"error: {invalid_filename} contains characters not in UTF-8"
    warning = f'warning: {warning_filename}: 1: avoid "using namespace std;"'
    assert output.index(invalid_file_error) < output.index(warning)
    assert SynchronousPool.callbacks == ["_proc_pipeline", "_proc_batch"]
