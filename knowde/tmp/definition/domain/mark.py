"""マークから定義名を抽出する関数群."""

from __future__ import annotations

import re

from knowde.tmp.definition.domain.errors import (
    EmptyMarkError,
    MarkContainsMarkError,
    PlaceHolderMappingError,
)

MARK_OPEN = "{"
MARK_CLOSE = "}"

MARK_PATTERN = re.compile(rf"\{MARK_OPEN}(.+?)\{MARK_CLOSE}")  # 非貪欲=最小マッチ


def pick_marks(s: str) -> list[str]:
    """マークの値を取り出す."""
    if not contains_mark_symbol(s):
        return []
    marks = MARK_PATTERN.findall(s)
    if any(map(contains_mark_symbol, marks)):
        msg = f"マーク内に'{MARK_OPEN}'または'{MARK_CLOSE}'が含まれています: {s}"
        raise MarkContainsMarkError(msg)
    if len(marks) == 0:
        msg = "マーク内に文字列を入力してください"
        raise EmptyMarkError(msg)
    return marks


def contains_mark_symbol(s: str) -> bool:
    """マーク文字を含むか."""
    return MARK_OPEN in s or MARK_CLOSE in s


PLACE_HOLDER = "$@"


def mark2placeholder(s: str) -> str:
    """markをplaceholderに置き換える."""
    return MARK_PATTERN.sub(PLACE_HOLDER, s)


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


def count_placeholder(s: str) -> int:
    """文字列に含まれるプレースホルダーを数える."""
    return s.count(PLACE_HOLDER)
