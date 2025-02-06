"""時系列.

時間の表現
    EDTF
    和暦
    期間の表現どうするか
        EDTF で 1950/2000 みたいに表現できるが分かりにくい気がする
        yyyy ~ yyyy
            がいい
        前者と後者をEDTFとして結合すればいい


"""
from __future__ import annotations

import time
from functools import cache
from typing import TYPE_CHECKING, Final, Iterable, Self

from intervaltree import Interval, IntervalTree
from more_itertools import flatten
from pydantic import BaseModel
from pyparsing import (
    Literal,
    ParserElement,
    Suppress,
    Word,
    printables,
)

from knowde.primitive.time.parse import parse_extime, str2edtf

if TYPE_CHECKING:
    from edtf import EDTFObject

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


def parse_when(string: str) -> EDTFObject:
    """時間指定(extimeの組み合わせ)をパース."""
    res = p_timespan().searchString(string)
    ls = list(flatten(res.asList()))
    if INTV_SEP not in ls:
        return parse_extime(string)
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


def edtf2interval(string: str) -> Interval:  # noqa: D103
    s, e = _when2span(string)
    return Interval(s, e, data=string)


def to_intvtree(strings: Iterable[str]) -> IntervalTree:
    """時間記述をIntervaltreeへ変換."""
    return IntervalTree([edtf2interval(s) for s in strings])


class Series(BaseModel, arbitrary_types_allowed=True):
    """時系列."""

    tree: IntervalTree

    @classmethod
    def create(cls, whens: Iterable[str]) -> Self:
        """Create from strings."""
        return cls(tree=to_intvtree(whens))

    def overlap(self, when: str) -> list[Interval]:
        """指定と重なる区間."""
        t: IntervalTree = self.tree  # なぜか補間が聞かないself.treeの代わり
        s, e = _when2span(when)
        return sorted(t.overlap(s, e))

    def envelop(self, when: str) -> list[Interval]:
        """指定に含まれる区間."""
        t: IntervalTree = self.tree  # なぜか補間が聞かないself.treeの代わり
        s, e = _when2span(when)
        return sorted(t.envelop(s, e))


def _when2span(when: str) -> tuple[float, float]:
    obj = parse_when(when)
    s = obj.lower_strict()
    e = obj.upper_strict()
    if s == e:
        e = _end_of_day(e)
    fs = s if s == float("-inf") else time.mktime(s)
    fe = e if e == float("inf") else time.mktime(e)
    return fs, fe


def _end_of_day(st: time.struct_time) -> time.struct_time:
    """同日のものをIntervalに変換するとstart == endとなってValueErrorになるのを回避."""
    return time.struct_time(
        (
            st.tm_year,
            st.tm_mon,
            st.tm_mday,
            23,
            59,
            59,
            st.tm_wday,
            st.tm_yday,
            st.tm_isdst,
        ),
    )
