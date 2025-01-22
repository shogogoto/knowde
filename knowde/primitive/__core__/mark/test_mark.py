"""mark test."""

import pytest

from . import PLACE_HOLDER, Marker, inject2placeholder
from .errors import EmptyMarkError, MarkContainsMarkError, PlaceHolderMappingError

BRACE_MARKER = Marker(m_open="{", m_close="}")  # 波括弧


def test_pick_mark() -> None:
    """文字列からマーク{}を識別する."""
    s1 = "xxx{def1}xxx"
    s2 = "{d1}x{d2}xxxx{d3}x"
    assert BRACE_MARKER.pick(s1) == ["def1"]
    assert BRACE_MARKER.pick(s2) == ["d1", "d2", "d3"]


def test_pick_mark_empty() -> None:
    """mark内が空の場合、抽出しない."""
    s = "xx{}xx"
    with pytest.raises(EmptyMarkError):
        BRACE_MARKER.pick(s)


def test_pick_mark_none() -> None:
    """markなし."""
    assert BRACE_MARKER.pick("xxx") == []


def test_pick_mark_in_mark() -> None:
    """markと同じ文字列を含む場合はエラー."""
    s1 = "{{}"
    s2 = "{}}"
    s3 = "{{}}"
    with pytest.raises(MarkContainsMarkError):
        BRACE_MARKER.pick(s1)

    with pytest.raises(MarkContainsMarkError):
        BRACE_MARKER.pick(s2)

    with pytest.raises(MarkContainsMarkError):
        BRACE_MARKER.pick(s3)


def test_replace_placeholder() -> None:
    """markをplaceholderへ置換."""
    s1 = "xx{def}xx"
    s2 = "xx{def}xx{def2}"

    assert BRACE_MARKER.replace(s1, PLACE_HOLDER) == "xx$@xx"
    assert BRACE_MARKER.replace(s2, *[PLACE_HOLDER] * 2) == "xx$@xx$@"


def test_inject2placeholder() -> None:
    """placeholderに文字を挿入."""
    s1 = "xx$@xx"
    s2 = "xx$@xx$@"  # $@ * 2
    assert inject2placeholder(s1, ["def"]) == "xxdefxx"
    assert inject2placeholder(s2, ["def", "def2"]) == "xxdefxxdef2"

    with pytest.raises(PlaceHolderMappingError):  # 2 != 1
        inject2placeholder(s2, ["d1"])

    with pytest.raises(PlaceHolderMappingError):  # 2 != 3
        inject2placeholder(s2, ["d1", "d2", "d3"])


def test_pick_nesting() -> None:
    """入れ子マーク."""
    m = Marker(m_open=r"\[", m_close=r"\]")
    s = "This is a [sample [nested] brace] str with [multiple [levels [of nesting]]]."
    assert m.pick_nesting(s) == [
        "sample [nested] brace",
        "multiple [levels [of nesting]]",
    ]


def test_marker_split() -> None:
    """マーク内を無視した分割."""
    # test_string = 'value1,"value2, still in quotes",value3,"another,value"'
    test_string = "value1,(value2, still in parentheses),value3,(another,value)"
    m = Marker(m_open="(", m_close=")")
    result = m.split(test_string, ",")
    assert result == [
        "value1",
        "(value2, still in parentheses)",
        "value3",
        "(another,value)",
    ]
