"""時系列."""


from enum import Enum, StrEnum
from typing import Final, Self

from edtf import EDTFObject, parse_edtf
from pydantic import BaseModel
from pyparsing import Char, Combine, Optional, Suppress, Word, nums


class MagicTime(StrEnum):
    """特殊時間文字."""

    BC = "BC"  # 紀元前 マイナスのエイリアス
    CENTURY = "C"  # 世紀 20C -> 1901/1/1 ~ 2000/12/31
    EARLY = "E"  # 前半
    MID = "M"  # 半ば
    LATE = "L"  # 後半


class Season(Enum):
    """季節."""

    SPRING = ("SP", "21")
    SUMMER = ("SU", "22")
    AUTUMN = ("A", "23")
    WINTER = ("W", "24")

    rep: str  # 文字列表現
    code: str  # EDTFコード

    def __init__(self, rep: str, code: str) -> None:  # noqa: D107
        self.rep = rep
        self.code = code


_pnumber: Final = Optional(Char("-")) + Word(nums)
_pcentury: Final = Combine(_pnumber + Suppress(MagicTime.CENTURY))


def str2edtf(s: str) -> str:
    """文字列をEDTF(Extended DateTime Format)に変換.

    区切り文字サポート [/-] e.g. yyyy[/MM[/dd]]
    """
    s = s.strip()
    if MagicTime.BC in s:
        s = s.replace(MagicTime.BC, "")
        s = f"-{s}"

    # 世紀 ex. 20C
    # BCの処理の前にやらないと"B"だけ残ったりでおかしくなる
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
        case _:
            return s


def to_year_edtf(s: str) -> str:
    """年のEDTF形式変換."""
    if _pnumber.matches(s):
        y = int(s)
        if abs(y) >= 10000:  # noqa: PLR2004
            return f"Y{y}"
        return f"{y:05}" if y < 0 else f"{y:04}"
    msg = f"'{s}'は年のフォーマットと合わない"
    raise ValueError(msg)


def parse_time(s: str) -> EDTFObject:
    """型ヒント用."""
    return parse_edtf(s)


class KnTime(BaseModel):
    """時刻."""

    val: str

    @classmethod
    def parse(cls, line: str) -> Self:
        """From string to time."""
        # t = Time(line)
        # print(t)
        return cls(val=line)

    # def to_time(self) -> None:
    #     pass

    def is_year(self) -> None:
        """年だけ."""
