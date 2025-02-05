"""期間.

スペースとチルダで結合された独自の日付表現
ex. yyy1/MM ~ yyy2/MM/dd
"""

from functools import cache
from typing import Final

from edtf import EDTFObject
from more_itertools import flatten
from pyparsing import (
    Literal,
    ParserElement,
    Suppress,
    Word,
    printables,
)

from knowde.primitive.time.parse import parse_extime, str2edtf

INTV_SEP: Final = "~"


@cache
def p_timespan() -> ParserElement:
    """Create a parser for patterns in the format."""
    edtf = Word("".join(c for c in printables if not c.isspace()))
    sep1, sep2, sep3 = (
        Suppress(Literal(s))
        for s in [
            f" {INTV_SEP} ",
            f"{INTV_SEP} ",
            f" {INTV_SEP}",
        ]
    )
    sep = sep1 | sep2 | sep3
    return edtf | edtf + sep + edtf | sep + edtf


def parse_when(s: str) -> EDTFObject:
    """時間指定(extimeの組み合わせ)をパース."""
    res = p_timespan().searchString(s)
    ls = list(flatten(res.asList()))
    if INTV_SEP not in ls:
        return parse_extime(s)
    i = ls.index(INTV_SEP)
    match (i, len(ls)):
        case (0, 2):  # ~ extime
            return parse_extime(f"../{ls[1]}")
        case (1, 2):  # ex1 ~
            return parse_extime(f"{ls[0]}/..")
        case (1, 3):  # ex1 ~ ex2
            f1 = str2edtf(ls[0])
            f2 = str2edtf(ls[2])
            return parse_extime(f"{f1}/{f2}")
        case _:
            raise ValueError
