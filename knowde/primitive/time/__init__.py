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
from collections.abc import Hashable, Iterable
from datetime import date, datetime
from functools import cache
from typing import TYPE_CHECKING, Final, Self

import edtf
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

from knowde.primitive.__core__.timeutil import TZ
from knowde.primitive.time.errors import EndBeforeStartError
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
            e = str2edtf(ls[1])
            return parse_extime(f"../{e}")
        case (1, 2):  # ex1 ~
            s = str2edtf(ls[0])
            return parse_extime(f"{s}/..")
        case (1, 3):  # ex1 ~ ex2
            f1 = str2edtf(ls[0])
            f2 = str2edtf(ls[2])
            e1 = parse_extime(f1)
            e2 = parse_extime(f2)
            if isinstance(e1, edtf.Interval):
                f1 = str(e1).split("/")[0]
            if isinstance(e2, edtf.Interval):
                f2 = str(e2).split("/")[-1]
            return parse_extime(f"{f1}/{f2}")
        case _:
            raise ValueError


class Series(BaseModel, arbitrary_types_allowed=True):
    """時系列."""

    tree: IntervalTree

    @classmethod
    def create(cls, whens: Iterable[Hashable]) -> Self:
        """Create from strings."""
        intvs = [Interval(*_when2span(str(s)), data=s) for s in whens]
        try:
            return cls(tree=IntervalTree(intvs))
        except ValueError as e:
            when = str(e).split(",")[-1].replace(")", "").strip()
            msg = "期間の終了が開始よりも早くて不正"
            raise EndBeforeStartError(msg, when) from e

    def overlap(self, when: str) -> list[Hashable]:
        """指定と重なる区間."""
        s, e = _when2span(when)
        intvs = sorted(self.tree.overlap(s, e))
        return [intv.data for intv in intvs]

    def envelop(self, when: str) -> list[Hashable]:
        """指定に含まれる区間."""
        s, e = _when2span(when)
        intvs = sorted(self.tree.envelop(s, e))
        return [intv.data for intv in intvs]

    @property
    def data(self) -> list[Hashable]:
        """全ての期間."""
        # t: IntervalTree = self.tree  # なぜか補間が聞かないself.treeの代わり
        intvs = sorted(self.tree.all_intervals)
        return [intv.data for intv in intvs]


def _when2span(when: str) -> tuple[float, float]:
    obj = parse_when(when)
    s = obj.lower_strict()
    e = obj.upper_strict()
    if s == e:
        e = _nudge_offset(e)
    fs = s if s == float("-inf") else time.mktime(s)
    fe = e if e == float("inf") else time.mktime(e)
    return fs, fe


def _nudge_offset(st: time.struct_time) -> time.struct_time:
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


def parse2dt(s: str) -> date:
    """Convert from string to date."""
    st = parse_when(s.strip()).lower_strict()
    t = time.mktime(st)
    return datetime.fromtimestamp(t, tz=TZ).date()
