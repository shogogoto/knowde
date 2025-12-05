"""indentエラーをテキストから探し出すのは大変."""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import TYPE_CHECKING

from lark.indenter import DedentError

from knowde.feature.parsing.tree_parser.errors import UnexpectedPivotError

if TYPE_CHECKING:
    from lark import Tree


def front_pivot(pivot: int, width: int) -> tuple[int, int]:
    """前側へ."""
    w = math.ceil(width / 2)
    return pivot - w, w


def rear_pivot(pivot: int, width: int) -> tuple[int, int]:
    """後ろ側へ."""
    w = math.ceil(width / 2)
    return pivot + w, w


def detect_undent(
    parse_fn: Callable[[str], Tree],
    lines: list[str],
    pivot: int,
    prev_width: int,
) -> int:
    """不完全なインデントがある行数を検知する."""
    if pivot <= 0 or pivot > len(lines):
        msg = f"pivot: {pivot}"
        raise UnexpectedPivotError(msg)
    part = "\n".join(lines[:pivot]) + "\n"
    try:
        parse_fn(part)
        next_, next_w = rear_pivot(pivot, prev_width)  # 検出しないから検索範囲拡大
    except DedentError:
        next_, next_w = front_pivot(pivot, prev_width)  # 検出したから検索範囲絞り込む
        if next_w == 1 and prev_width == 1:
            return next_  # 前回OK 今回NG

    return detect_undent(parse_fn, lines, next_, next_w)
