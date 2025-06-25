"""定数系."""

from enum import Enum, StrEnum
from typing import Final

from pyparsing import Char, Combine, Optional, Suppress, Word, nums


class MagicTime(StrEnum):
    """特殊時間文字."""

    BC = "BC"  # 紀元前 マイナスのエイリアス
    CENTURY = "C"  # 世紀 20C -> 1901/1/1 ~ 2000/12/31


p_number: Final = Optional(Char("-")) + Word(nums)
p_century: Final = Combine(p_number + Suppress(MagicTime.CENTURY))


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

        if not p_century.matches(txt):
            msg = f"'{season}'は世紀とのみ併用できます."
            raise ValueError(msg, string)
        n = p_century.parse_string(txt)[0]
        n = int(n) * 100
        if n > 0:
            return f"{n:04}-{season.code}"
        return f"{n:05}-{season.code}"  # マイナスの分１つゼロ多く
