"""test term domain."""
from __future__ import annotations

import pytest

from . import (
    MergedTerms,
    Term,
    next_lookup,
)
from .errors import (
    AliasContainsMarkError,
    MarkUncontainedError,
    TermConflictError,
    TermResolveError,
)


def test_alias_error() -> None:
    """Alias contains marks."""
    with pytest.raises(AliasContainsMarkError):
        Term.create(alias="a{b}")


def test_term_str() -> None:
    """String."""
    t1 = Term.create("X", "x1", "x2")
    t2 = Term.create("Y", "y1")
    t3 = Term.create("Z")
    t4 = Term.create("U", alias="P1")
    t5 = Term.create("V", "v1", alias="P1")
    t6 = Term.create(alias="P1")
    t7 = Term.create("B{A}")
    assert str(t1) in ["X(x1, x2)", "X(x2, x1)"]
    assert str(t2) == "Y(y1)"
    assert str(t3) == "Z"
    assert str(t4) == "U[P1]"
    assert str(t5) == "V(v1)[P1]"
    assert str(t6) == "[P1]"
    assert str(t7) == "B{A}"


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


def test_lookup() -> None:
    """参照."""
    mt = MergedTerms()
    t1 = Term.create("A", alias="a")
    t2 = Term.create("A1", "A2")
    t3 = Term.create("B{A}")
    t4 = Term.create("C{BA}")
    mt.add(t1, t2, t3, t4)
    # 0th
    assert mt.atoms == {"A": t1, "a": t1, "A1": t2, "A2": t2}
    # 1th
    l1, _ = next_lookup(mt.atoms, mt.frozen)
    assert l1 == {"BA": t3}
    # 2th
    d = {**mt.atoms, **l1}
    l2, _ = next_lookup(d, mt.frozen)
    assert l2 == {"CBA": t4}

    # 3th
    d = {**d, **l2}
    l3, _ = next_lookup(d, mt.frozen)
    assert l3 == {}


def test_lookup_error() -> None:
    """参照失敗."""
    mt = MergedTerms()
    mt.add(
        Term.create("A", alias="a"),
        Term.create("A1", "A2"),
        Term.create("B{A}"),
        Term.create("C{A1}"),
        Term.create("D{BA}"),
        Term.create("xx{X}xx"),
    )
    with pytest.raises(TermResolveError):
        mt.to_resolver()


def test_resolve_term() -> None:
    """用語解決."""
    t1 = Term.create("A", alias="a")
    t2 = Term.create("A1", "A2")
    t3 = Term.create("B{A}")
    t4 = Term.create("C{A1}")
    t5 = Term.create("D{BA}")
    t6 = Term.create("E{DBA}")
    resolver = MergedTerms().add(t1, t2, t3, t4, t5, t6).to_resolver()
    d = resolver("aaa{EDBA}a{CA1}aaa")
    assert d == {
        "EDBA": {"DBA": {"BA": {"A": {}}}},
        "CA1": {"A1": {}},
    }
    assert resolver.mark2term(d) == {
        t6: {t5: {t3: {t1: {}}}},
        t4: {t2: {}},
    }

    with pytest.raises(MarkUncontainedError):
        resolver("x{uncontained}x")
