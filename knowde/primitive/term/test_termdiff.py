"""test."""
import pytest

from knowde.primitive.term import MergedTerms, Term
from knowde.primitive.term.errors import MarkUncontainedError
from knowde.primitive.term.termdiff import (
    get_lookup,
    get_refer_terms,
    to_lookup,
)


def test_lookup_refactored() -> None:
    """参照なし用語を取得2."""
    mt = MergedTerms()
    t1 = Term.create("A", alias="a")
    t2 = Term.create("A1", "A2")
    t3 = Term.create("B{A}")
    t4 = Term.create("C{BA}")
    t5 = Term.create(alias="only")
    t6 = Term.create("D{A1}", alias="not0th")
    mt.add(t1, t2, t3, t4, t5, t6)
    s = set(mt.terms)
    # 0th
    assert mt.no_referred == {t1, t2, t5}  # 参照なし
    assert get_lookup(mt.no_referred) == {
        "A": t1,
        "a": t1,
        "A1": t2,
        "A2": t2,
        "only": t5,
    }
    # 1th
    r1 = get_refer_terms(s, mt.no_referred)
    assert r1 == {t3, t6}
    assert get_lookup(r1) == {"BA": t3, "DA1": t6, "not0th": t6}
    # 2th
    rd = frozenset({*r1, *mt.no_referred})
    r2 = get_refer_terms(s, rd)
    assert r2 == {t4}
    assert get_lookup(r2) == {"CBA": t4}
    # 3th
    rd2 = frozenset({*r2, *rd})
    r3 = get_refer_terms(s, rd2)
    assert get_lookup(r3) == {}


def test_no_refer() -> None:
    """."""
    mt = MergedTerms()
    t1 = Term.create("Y{X}", alias="not_exist")  # 参照がない場合
    t2 = Term.create("P")  # 参照がない場合
    t3 = Term.create("A")
    t4 = Term.create("B{A}")
    t5 = Term.create("C{BA}")
    mt.add(t1, t2, t3, t4, t5)
    s = set(mt.terms)
    # 0th
    assert mt.no_referred == {t2, t3}
    # 1th
    r1 = get_refer_terms(s, mt.no_referred)
    assert r1 == {t4}
    # 2th
    rd = frozenset({*r1, *mt.no_referred})
    r2 = get_refer_terms(s, rd)
    assert r2 == {t5}
    # 3th
    rd2 = frozenset({*r2, *rd})
    r3 = get_refer_terms(s, rd2)
    assert get_lookup(r3) == {}

    # 残る
    assert s - rd2 == {t1}


def test_to_lookup() -> None:
    """markの依存関係."""
    t1 = Term.create("A", alias="a")
    t2 = Term.create("A1", "A2")
    t3 = Term.create("B{A}")
    t4 = Term.create("C{A1}")
    t5 = Term.create("D{BA}")
    t6 = Term.create("E{DBA}")
    # ex = Term.create("X{Y}")
    mt = MergedTerms().add(t1, t2, t3, t4, t5, t6)
    # ╟── a
    # ╟── A2
    # ╟── CA1
    # ╎   └─╼ A1
    # ╙── EDBA
    #    └─╼ DBA
    #        └─╼ BA
    #            └─╼ A
    assert to_lookup(mt.frozen) == {
        "a": t1,
        "A": t1,
        "A2": t2,
        "A1": t2,
        "BA": t3,
        "CA1": t4,
        "DBA": t5,
        "EDBA": t6,
    }


def test_to_lookup_with_unmarked() -> None:
    """参照が存在しない."""
    t1 = Term.create("A", alias="a")
    t2 = Term.create("A1", "A2")
    t3 = Term.create("B{A}")
    ex = Term.create("X{Y}")
    mt = MergedTerms().add(ex)
    with pytest.raises(MarkUncontainedError):
        to_lookup(mt.frozen)

    ex = Term.create("X{Y}")
    mt2 = MergedTerms().add(t1, t2, t3, ex)
    with pytest.raises(MarkUncontainedError):
        to_lookup(mt2.frozen)
