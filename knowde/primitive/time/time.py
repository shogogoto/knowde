"""時系列."""
from enum import Enum, StrEnum
from typing import Final, Self

from edtf import EDTFObject, parse_edtf
from pydantic import BaseModel
from pyparsing import (
    Char,
    Combine,
    Forward,
    Literal,
    Optional,
    Suppress,
    Word,
    nums,
)


def pinterval() -> Forward:
    """EDTFのintervalを判別."""
    slash = Literal("/")
    dots = Literal("..")
    hyphen = Literal("-")

    year = Optional(hyphen) + Word(nums, exact=4)
    month = Word(nums, min=1, max=2)
    day = Word(nums, min=1, max=2)
    date = year + Optional(hyphen + month + Optional(hyphen + day))

    date_range = Forward()
    date_range << (
        (date + slash + date)  # 1964/2008
        | (date + slash + dots)  # open end ex. 1985/..
        | (dots + slash + date)  # open start ex.  ../1985
    )

    return date_range


class MagicTime(StrEnum):
    """特殊時間文字."""

    BC = "BC"  # 紀元前 マイナスのエイリアス
    CENTURY = "C"  # 世紀 20C -> 1901/1/1 ~ 2000/12/31


class Season(Enum):
    """季節EDTF. yyyy-[code]."""

    SPRING = ("SPRING", "21")
    SUMMER = ("SUMMER", "22")
    AUTUMN = ("AUTUMN", "23")
    WINTER = ("WINTER", "24")

    EARLY = ("EARLY", "37")  # 前半 1 ~ 4 月
    MID = ("MID", "38")  # 半ば 5 ~ 8 月
    LATE = ("LATE", "39")  # 後半 9 ~ 12 月

    rep: str  # 文字列表現
    code: str  # EDTFコード

    def __init__(self, rep: str, code: str) -> None:  # noqa: D107
        self.rep = rep
        self.code = code

    @classmethod
    def replace(cls, string: str) -> str:
        """n世紀に拡張月(code)を付加."""
        txt = string
        season = None
        for s in cls:
            if s.rep in txt:
                season = s
                txt = txt.replace(s.rep, "")
                break
        if season is None:
            return string

        if not _pcentury.matches(txt):
            msg = f"'{season}'は世紀とのみ併用できます."
            raise ValueError(msg, string)
        n = _pcentury.parse_string(txt)[0]
        n = int(n) * 100
        if n > 0:
            return f"{n:04}-{season.code}"
        return f"{n:05}-{season.code}"  # マイナスの分１つゼロ多く

        #     s = season.replace(s)


_pnumber: Final = Optional(Char("-")) + Word(nums)
_pcentury: Final = Combine(_pnumber + Suppress(MagicTime.CENTURY))
_pinterval: Final = pinterval()


def str2edtf(string: str) -> str:
    """文字列をEDTF(Extended DateTime Format)に変換.

    区切り文字サポート [/-] e.g. yyyy[/MM[/dd]]
    """
    s = string.strip().replace(" ", "")
    if MagicTime.BC in s:
        s = s.replace(MagicTime.BC, "")
        s = f"-{s}"

    # 世紀 ex. 20C
    # BCの処理の前にやらないと"B"だけ残ったりでおかしくなる
    # 20C -> 1901/2000 が厳密だが、19XXでよくね?
    s = Season.replace(s)
    if _pcentury.matches(s):
        n = _pcentury.parse_string(s)[0]
        n = int(n)
        if n > 0:
            c0 = n * 100 - 99
            c1 = n * 100
            return f"{c0:04}/{c1:04}"
        c0 = n * 100 + 1
        c1 = n * 100 + 100
        return f"{c0:05}/{c1:05}"

    if _pinterval.matches(s):
        return s

    if s[0] == "-":
        ymd = s[1:].replace("/", "-").split("-", maxsplit=1)
        ymd[0] = f"-{ymd[0]}"
    else:
        ymd = s.replace("/", "-").split("-", maxsplit=1)
    match len(ymd):
        case 1:
            return to_year_edtf(ymd[0])
        case 2:
            y, md = ymd
            y = to_year_edtf(y)
            md = [e.zfill(2) for e in md.split("-")]
            return "-".join([y, *md])
        case 3:
            y, m, d = ymd
            return s
        case _:
            raise ValueError(string)


def to_year_edtf(s: str) -> str:
    """年のEDTF形式変換."""
    if _pnumber.matches(s):
        y = int(s)
        if abs(y) >= 10000:  # noqa: PLR2004
            return f"Y{y}"
        return f"{y:05}" if y < 0 else f"{y:04}"
    # s2 = text_to_edtf(s)
    # if s2 is None:
    #     msg = f"'{s}'は年のフォーマットと合わない"
    #     raise ValueError(msg)
    return s


def parse_time(s: str) -> EDTFObject:
    """型ヒント用."""
    return parse_edtf(s)


class KnTime(BaseModel):
    """時刻."""

    val: str

    @classmethod
    def parse(cls, line: str) -> Self:
        """From string to time."""
        return cls(val=line)
