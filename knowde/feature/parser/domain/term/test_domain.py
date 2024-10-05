"""test term domain."""


import pytest

from knowde.feature.parser.domain.term.domain import (
    Term,
    TermConflictError,
    TermMergeError,
    TermSpace,
)

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
    assert str(t1) == "X(x1, x2)"
    assert str(t2) == "Y(y1)"
    assert str(t3) == "Z"


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


def test_term_allows_merge() -> None:
    """用語の結合を許す場合."""
    # 共通あり
    t1 = Term.create("X", "x1")
    t2 = Term.create("X", "x2")
    assert t1.allows_merge(t2)

    ## 共通あっても単一名はダメ
    t3 = Term.create("X")
    assert not t1.allows_merge(t3)
    with pytest.raises(TermMergeError):
        t1.merge(t3)
    # 共通なし
    t4 = Term.create("Y")
    assert not t1.allows_merge(t4)


def test_termspace_add() -> None:
    """用語空間に用語を追加."""
    s = TermSpace()
    # 共通ありで合併
    t1 = Term.create("X", "x1")
    t2 = Term.create("X", "x2")
    s.add(t1)
    s.add(t2)
    assert len(s) == 1
    assert s[0] == Term.create("X", "x1", "x2")

    # 重複の追加はエラー
    with pytest.raises(TermConflictError):
        s.add(t2)

    # 共通なしの追加
    t3 = Term.create("Y")
    s.add(t3)
    assert len(s) == 2  # noqa: PLR2004

    # 共通あっても単一名はダメ
    with pytest.raises(TermMergeError):
        s.add(Term.create("X"))
