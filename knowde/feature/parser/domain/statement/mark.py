"""マークから定義名を抽出する関数群."""
from __future__ import annotations

import re
from typing import Final

from .errors import (
    EmptyMarkError,
    MarkContainsMarkError,
    PlaceHolderMappingError,
)

BRACE_OPEN: Final = "{"
BRACE_CLOSE: Final = "}"
# 非貪欲=最小マッチ
MARK_PATTERN: Final = re.compile(rf"\{BRACE_OPEN}(.+?)\{BRACE_CLOSE}")
HOLDER: Final = "%@"


def pick_marks(s: str) -> list[str]:
    """マークの値を取り出す."""
    if not contains_mark_symbol(s):
        return []
    marks = MARK_PATTERN.findall(s)
    if any(map(contains_mark_symbol, marks)):
        msg = f"マーク内に'{BRACE_OPEN}'または'{BRACE_CLOSE}'が含まれています: {s}"
        raise MarkContainsMarkError(msg)
    if len(marks) == 0:
        msg = "マーク内に文字列を入力してください"
        raise EmptyMarkError(msg)
    return marks


def contains_mark_symbol(s: str) -> bool:
    """マーク文字を含むか."""
    return BRACE_OPEN in s or BRACE_CLOSE in s


def mark2holder(s: str) -> str:
    """markをplaceholderに置き換える."""
    return MARK_PATTERN.sub(HOLDER, s)


def inject2holder(
    s: str,
    values: list[str],
    prefix: str = "",
    suffix: str = "",
) -> str:
    """プレースホルダーに順次文字列を埋め込む."""
    ret = s
    n_ph = ret.count(HOLDER)
    n_v = len(values)
    if n_ph != n_v:
        msg = f"プレースホルダー数{ret} != 置換する値の数{values}"
        raise PlaceHolderMappingError(msg)
    c = re.compile(rf"{HOLDER}")
    for v in values:
        ret = c.sub(prefix + v + suffix, ret, count=1)
    return ret


def count_holder(s: str) -> int:
    """文字列に含まれるプレースホルダーを数える."""
    return s.count(HOLDER)
