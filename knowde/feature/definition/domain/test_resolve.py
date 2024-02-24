"""explainを定義と紐付ける."""


import pytest

from knowde.feature.definition.domain.errors import MarkContainsMarkError
from knowde.feature.definition.domain.resolve import inject_mark, pick_mark


def test_parse_mark() -> None:
    """文字列からマーク{}を識別する."""
    s1 = "xxx{def1}xxx"
    s2 = "{d1}x{d2}xxxx{d3}x"
    assert pick_mark(s1) == ["def1"]
    assert pick_mark(s2) == ["d1", "d2", "d3"]


def test_parse_mark_empty() -> None:
    """mark内が空の場合、抽出しない."""
    txt = "xx{}xx"
    assert pick_mark(txt) == []


def test_parse_mark_in_mark() -> None:
    """markと同じ文字列を含む場合はエラー."""
    txt1 = r"{{}"
    txt2 = r"{}}"
    txt3 = r"{{}}"
    with pytest.raises(MarkContainsMarkError):
        pick_mark(txt1)

    with pytest.raises(MarkContainsMarkError):
        pick_mark(txt2)

    with pytest.raises(MarkContainsMarkError):
        pick_mark(txt3)


# def test_inject_mark() -> None:
#     txt = "xx{}xx"
#     assert inject_mark(txt, "@") == "xx@xx"
