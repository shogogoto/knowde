"""mark domain."""

from __future__ import annotations

import re
from functools import cached_property
from typing import Final

from pydantic import BaseModel

from .errors import (
    EmptyMarkError,
    MarkContainsMarkError,
    PlaceHolderMappingError,
)

MARK_OPEN: Final = "{"
MARK_CLOSE: Final = "}"

MARK_PATTERN: Final = re.compile(rf"\{MARK_OPEN}(.+?)\{MARK_CLOSE}")


class Marker(BaseModel, frozen=True):
    """マークロジック."""

    m_open: str
    m_close: str

    @cached_property
    def pattern(self) -> re.Pattern[str]:
        """非貪欲=最小マッチ."""
        return re.compile(rf"\{self.m_open}(.+?)\{self.m_close}")

    def pick(self, s: str) -> list[str]:
        """マークの値を取り出す."""
        if not self.contains_symbol(s):
            return []
        marks = self.pattern.findall(s)
        if any(map(self.contains_symbol, marks)):
            msg = (
                f"マーク内に'{self.m_open}'または'{self.m_close}'が含まれています: {s}"
            )
            raise MarkContainsMarkError(msg)
        if len(marks) == 0:
            msg = "マーク内に文字列を入力してください"
            raise EmptyMarkError(msg)
        return marks

    def contains_symbol(self, s: str) -> bool:
        """マーク文字を含むか."""
        return self.m_open in s or self.m_close in s

    def replace(self, s: str, *repls: str) -> str:
        """markを置き換える."""
        ret = s
        for repl in repls:
            ret = self.pattern.sub(repl, ret, count=1)
        return ret


BRACE_MARKER: Final = Marker(m_open=MARK_OPEN, m_close=MARK_CLOSE)

PLACE_HOLDER: Final = "$@"


def inject2placeholder(
    s: str,
    values: list[str],
    prefix: str = "",
    suffix: str = "",
) -> str:
    """プレースホルダーに順次文字列を埋め込む."""
    ret = s
    n_ph = ret.count(PLACE_HOLDER)
    n_v = len(values)
    if n_ph != n_v:
        msg = f"プレースホルダー数{ret} != 置換する値の数{values}"
        raise PlaceHolderMappingError(msg)
    c = re.compile(r"\$\@")
    for v in values:
        ret = c.sub(prefix + v + suffix, ret, count=1)
    return ret
