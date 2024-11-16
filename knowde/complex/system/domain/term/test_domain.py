"""test term domain."""
from __future__ import annotations

import pytest

from .domain import (
    MergedTerms,
    Term,
)
from .errors import TermConflictError

"""
Termは名前の集合に与える識別子
A=B=C:
は {A, B, C} -> term -> 言明
という中間層

重複した名の宣言は禁止
ただし、実はこの名も宣言済みの名と同じ概念であることが読書のあとになって発覚する場合がある

一覧のスコープ:
    ソースごと
    見出しごと

表示形式:
    言明付き
    言明の依存関係情報
"""


def test_term_str() -> None:
    """String."""
    t1 = Term.create("X", "x1", "x2")
    t2 = Term.create("Y", "y1")
    t3 = Term.create("Z")
    t4 = Term.create("U", alias="P1")
    t5 = Term.create("V", "v1", alias="P1")
    t6 = Term.create(alias="P1")
    assert str(t1) == "X(x1, x2)"
    assert str(t2) == "Y(y1)"
    assert str(t3) == "Z"
    assert str(t4) == "U[P1]"
    assert str(t5) == "V(v1)[P1]"
    assert str(t6) == "[P1]"


def test_term_has_common() -> None:
    """同じ名前を持つ用語."""
    t1 = Term.create("X", "x1")
    t2 = Term.create("X")
    assert t1.has(*t2.names)
    assert t2.has(*t1.names)

    t3 = Term.create("Y")
    assert not t1.has(*t3.names)
    assert not t2.has(*t3.names)
    assert not t3.has(*t1.names)
    assert not t3.has(*t2.names)


@pytest.mark.parametrize(
    ("names1", "names2", "alias1", "alias2", "expected"),
    [
        # aliasなし
        (("X", "x1"), ("X", "x2"), None, None, True),  # 共通あり
        (("X", "x1"), ("X"), None, None, True),  # 共通あり 片方単一名OK
        (("X"), ("X"), None, None, False),  # 共通あり 両方単一名NG
        (("X",), ("Y",), None, None, False),  # 共通なし
        # alias 片方
        (("X", "x1"), ("X", "x2"), "P1", None, True),  # 共通あり
        (("X", "x1"), ("X"), "P1", None, True),  # 共通あり 片方単一名OK
        (("X"), ("X"), "P1", None, False),  # 共通あり 両方単一名NG
        (("X",), ("Y",), "P1", None, False),  # 共通なし
        # alias 両方
        (("X", "x1"), ("X", "x2"), "P1", "P2", False),  # 共通あり
        (("X", "x1"), ("X"), "P1", "P2", False),  # 共通あり 片方単一名OK
        (("X"), ("X"), "P1", "P2", False),  # 共通あり 両方単一名NG
        (("X",), ("Y",), "P1", "P2", False),  # 共通なし
        # aliasのみ
        ((), (), "P1", None, False),
        ((), (), "P1", "P2", False),
    ],
)
def test_term_with_alias_allows_merge(
    names1: tuple[str],
    names2: tuple[str],
    alias1: str,
    alias2: str,
    expected: bool,  # noqa: FBT001
) -> None:
    """別名ありの用語での結合の許可."""
    t1 = Term.create(*names1, alias=alias1)
    t2 = Term.create(*names2, alias=alias2)
    assert t1.allows_merge(t2) == expected
    assert t2.allows_merge(t1) == expected


def test_merge_term() -> None:
    """用語をマージ."""
    s = MergedTerms()
    # 共通ありで合併
    t1 = Term.create("X", "x1")
    t2 = Term.create("X", "x2")
    s.add(t1)
    s.add(t2)
    assert len(s) == 1
    assert s[0] == Term.create("X", "x1", "x2")

    with pytest.raises(TermConflictError):  # 重複の追加はエラー
        s.add(t2)

    # 共通なしの追加
    t3 = Term.create("Y")
    s.add(t3)
    assert len(s) == 2  # noqa: PLR2004
