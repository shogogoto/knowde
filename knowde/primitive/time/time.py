"""時系列."""


import re
from enum import StrEnum
from typing import Final, Self

from edtf import EDTFObject, parse_edtf
from pydantic import BaseModel
from pyparsing import Optional, Suppress, Word, nums

TS_PT: Final = r"(^-?\d+)?(\/\d+)?(\/\d+)?(@.+)?"
TS_RE: Final = re.compile(TS_PT)


pnumber = Optional(Suppress("-")) + Word(nums)


def parse_time(s: str) -> EDTFObject:
    """型ヒント用."""
    return parse_edtf(s)


def align4edtf(s: str) -> str:
    """文字列をEDTF(Extended DateTime Format)に変換できるよう整形.

    区切り文字サポート [/-] e.g. yyyy[/MM[/dd]]
    """
    is_minus = False
    if s[0] == "-":  # マイナス年
        is_minus = True
        s = s[1:]

    ymd = s.strip().replace("/", "-").split("-", maxsplit=1)
    match len(ymd):
        case 1:
            y = ymd[0]
            return f"-{y:0>4}" if is_minus else f"{y:0>4}"
        case 2:
            y, md = ymd
            y = f"-{y:0>4}" if is_minus else f"{y:0>4}"
            md = [e.zfill(2) for e in md.split("-")]
            return "-".join([y, *md])
        case _:
            raise ValueError(s, ymd)


class MagicTimeStr(StrEnum):
    """特殊文字."""

    BC = "BC"  # 紀元前 マイナスのエイリアス
    CENTURY = "C"  # 世紀 20C -> 1901/1/1 ~ 2000/12/31
    EARLY = "E"  # 前半
    MID = "M"  # 半ば
    LATE = "L"  # 後半


class Span(BaseModel):
    """時間幅.

    単一時刻はstart == endとする時刻の拡張
    """

    # @classmethod
    # def from_y(cls, year: int) -> Self:
    #     """年."""

    # @classmethod
    # def from_ym(cls, year, int, month: int) -> Self:
    #     """年月."""


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
