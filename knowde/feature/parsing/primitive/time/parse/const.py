"""定数系."""

from enum import Enum, StrEnum
from typing import Final, Self

from pyparsing import Char, Combine, Optional, Suppress, Word, nums

from knowde.feature.parsing.primitive.time.errors import ParseWhenError


class MagicTime(StrEnum):
    """特殊時間文字."""

    BC = "BC"  # 紀元前 マイナスのエイリアス
    CENTURY = "C"  # 世紀 20C -> 1901/1/1 ~ 2000/12/31


P_NUMBER: Final = Optional(Char("-")) + Word(nums)
P_CENTURY: Final = Combine(P_NUMBER + Suppress(MagicTime.CENTURY))


class Season(Enum):
    """季節EDTF. yyyy-[code]."""

    EARLY = ("EARLY", 0)  # 初頭
    MID = ("MID", 40)  # 半ば
    LATE = ("LATE", 80)  # 終わり頃

    rep: str  # 文字列表現
    offset: int
    width: int

    def __init__(self, rep: str, offest: int) -> None:  # noqa: D107
        self.rep = rep
        self.offset = offest
        self.width = 20

    @classmethod
    def replace(cls, string: str) -> tuple[str, Self | None]:
        """n世紀に拡張月(code)を付加."""
        txt = string
        season = None
        for s in cls:
            if s.rep in txt:
                season = s
                txt = txt.replace(s.rep, "")
                break
        if season is None:
            return string, None

        if not P_CENTURY.matches(txt):
            msg = f"'{season}'は世紀とのみ併用できます."
            raise ParseWhenError(msg, string)
        return txt, season


def century2span(s: str) -> tuple[int, int]:
    """世紀をstart, end に変換."""
    n = P_CENTURY.parse_string(s)[0]
    n = int(str(n))
    if n > 0:
        start = n * 100 - 99
        end = n * 100
    else:
        start = n * 100 + 1
        end = n * 100 + 100
    return start, end
