"""test."""


from pathlib import Path

from . import Versioning


def test_version_add(tmp_path: Path) -> None:
    """Version add."""
    txt = "aaa"
    v = Versioning(name="hoge", root_dir=tmp_path)
    assert v.versions == []
    assert v.latest == 0
    v.add(txt)
    assert v.latest == 1
    v.add(txt)
    assert v.latest == 1
    v.add("bbb")
    assert v.latest == 2  # noqa: PLR2004
