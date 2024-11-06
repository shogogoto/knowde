"""説明を定義と紐付ける.

説明を表す文字列に定義を埋め込んで表現できるようにしたい
"""


import pytest

from .errors import (
    EmptyMarkError,
    MarkContainsMarkError,
    PlaceHolderMappingError,
)
from .mark import (
    HOLDER,
    count_holder,
    inject2holder,
    mark2holder,
    pick_marks,
)


def test_pick_mark() -> None:
    """文字列からマーク{}を識別する."""
    s1 = "xxx{def1}xxx"
    s2 = "{d1}x{d2}xxxx{d3}x"
    assert pick_marks(s1) == ["def1"]
    assert pick_marks(s2) == ["d1", "d2", "d3"]


def test_pick_mark_empty() -> None:
    """mark内が空の場合."""
    s = "xx{}xx"
    with pytest.raises(EmptyMarkError):
        pick_marks(s)


def test_pick_mark_none() -> None:
    """markなし."""
    assert pick_marks("xxx") == []


def test_pick_mark_in_mark() -> None:
    """markと同じ文字列を含む場合はエラー."""
    s1 = "{{}"
    s2 = "{}}"
    s3 = "{{}}"
    with pytest.raises(MarkContainsMarkError):
        pick_marks(s1)

    with pytest.raises(MarkContainsMarkError):
        pick_marks(s2)

    with pytest.raises(MarkContainsMarkError):
        pick_marks(s3)


def test_replace_marks() -> None:
    """markをplaceholderへ置換."""
    s1 = "xx{def}xx"
    s2 = "xx{def}xx{def2}"

    assert mark2holder(s1) == f"xx{HOLDER}xx"
    assert mark2holder(s2) == f"xx{HOLDER}xx{HOLDER}"


def test_count_place_holder() -> None:
    """プレースホルダーを数える."""
    assert count_holder("xx%x@xx") == 0
    assert count_holder(f"xx{HOLDER}xx") == 1
    assert count_holder(f"xx{HOLDER}{HOLDER}") == 2  # noqa: PLR2004


def test_inject2placeholder() -> None:
    """placeholderに文字を挿入."""
    s1 = f"xx{HOLDER}xx"
    s2 = f"xx{HOLDER}xx{HOLDER}"  # {HOLDER} * 2
    assert inject2holder(s1, ["def"]) == "xxdefxx"
    assert inject2holder(s2, ["def", "def2"]) == "xxdefxxdef2"

    with pytest.raises(PlaceHolderMappingError):  # 2 != 1
        inject2holder(s2, ["d1"])

    with pytest.raises(PlaceHolderMappingError):  # 2 != 3
        inject2holder(s2, ["d1", "d2", "d3"])
