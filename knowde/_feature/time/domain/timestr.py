from __future__ import annotations

import re

from pydantic import BaseModel, Field

from .const import SOCIETY_TIMELINE
from .domain import TimeValue

NULL_EXPRESSION = "99"


def to_int(v: str | None) -> int | None:
    """人生日付文字列 to int."""
    if v == "" or v is None:
        return None
    return int(v.replace("/", ""))


TS_PT = r"(^-?\d+)?(\/\d+)?(\/\d+)?(@.+)?"
TS_RE = re.compile(TS_PT)


class TimeStr(BaseModel, frozen=True):
    """時刻の文字列表現.

    月日を指定しなくてもいいようにしたいがdatetimeだけでは無理
    区切り文字がないとyyMMddやyyyyMMを区別できない
    e.g.
        1999/01/01
        1999/01
        1999
        1999@AD
        @AD
    """

    value: str = Field(pattern=TS_PT)

    @property
    def val(self) -> TimeValue:
        gs = TS_RE.findall(self.value)[0]
        if len(gs) != 4:  # noqa: PLR2004
            raise ValueError
        y = to_int(gs[0])
        m = to_int(gs[1])
        d = to_int(gs[2])
        tl = gs[3][1:] if gs[3] != "" else SOCIETY_TIMELINE
        return TimeValue.new(tl, y, m, d)
