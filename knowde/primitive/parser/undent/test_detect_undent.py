"""test."""

from textwrap import dedent

import pytest
from lark.indenter import DedentError

from knowde.primitive.parser import create_parser
from knowde.primitive.parser.errors import UnexpectedPivotError

from . import detect_undent, front_pivot

_t1 = """
# h
"""
_t2 = """
# h
    aaa
"""
_t3 = """
# h
    aaa
     bbb
"""


@pytest.mark.parametrize(
    "txt",
    [
        pytest.param(_t1, id="1l"),
        pytest.param(_t2, id="2l"),
        pytest.param(_t3, id="3l"),
    ],
)
def test_no_undent(txt: str) -> None:
    """不完全インデント検出なし."""
    s = dedent(txt)
    lines = s.splitlines()
    pivot, w = front_pivot(len(lines), len(lines))
    create_parser().parse(s)  # DedentErrorそもそも起きない
    with pytest.raises(UnexpectedPivotError):
        detect_undent(create_parser().parse, lines, pivot, w)


_t4 = """
# h
    aaa
   bbb
"""
_t5 = """
# h
    aaa
   bbb
   ccc
"""
_t6 = """
# h
    aaa
   bbb
   ccc
   ddd
"""
_t7 = """
# h
   aaa
     bbb
    ccc
   ddd
"""
_t8 = """
# h
   aaa
   bbb
     ccc
    ddd
"""


@pytest.mark.parametrize(
    ("txt", "expected"),
    [
        pytest.param(_t4, 2, id="3lines aaa"),
        pytest.param(_t5, 2, id="4lines aaa"),
        pytest.param(_t6, 2, id="5lines aaa"),
        pytest.param(_t7, 3, id="5lines bbb"),
        pytest.param(_t8, 4, id="5lines ccc"),
    ],
)
def test_detect_undent(txt: str, expected: int) -> None:
    """不完全インデント検出."""
    s = dedent(txt).strip()
    with pytest.raises(DedentError):
        create_parser().parse(s)
    lines = s.splitlines()
    pivot, w = front_pivot(len(lines), len(lines))
    i = detect_undent(create_parser().parse, lines, pivot, w)
    assert i == expected
