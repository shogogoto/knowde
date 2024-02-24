"""マークから定義名を抽出する."""
from __future__ import annotations

import re

from knowde.feature.definition.domain.errors import MarkContainsMarkError

MARK_OPEN = "{"
MARK_CLOSE = "}"


def pick_mark(s: str) -> list[str]:
    """Parse marks."""
    pattern = rf"\{MARK_OPEN}(.+?)\{MARK_CLOSE}"  # 非貪欲=最小マッチ
    marks = re.findall(pattern, s)
    if any(map(contains_mark, marks)):
        msg = f"マーク内にマーク文字'{MARK_OPEN}'または'{MARK_CLOSE}'が含まれています: {s}"
        raise MarkContainsMarkError(msg)
    return marks


def contains_mark(s: str) -> bool:
    """マークを含むか."""
    return MARK_OPEN in s or MARK_CLOSE in s


# def inject_mark(txt: str, content: str) -> str:
#     pass
