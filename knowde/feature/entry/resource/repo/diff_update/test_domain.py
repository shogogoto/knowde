"""差分更新test."""

from knowde.feature.parsing.primitive.term import Term
from knowde.feature.parsing.tree2net import parse2net
from knowde.shared.nxutil.edge_type import EdgeType

from .domain import (
    UpdateDiff,
    create_edgediff,
    identify_sentence,
    identify_term,
)


def test_term_diff() -> None:
    """用語差分."""
    s1 = """
        # title
            A: a
            B: b
            c
    """
    s2 = """
        # title
            B: b
            c
            D: d
    """

    sn1 = parse2net(s1)
    sn2 = parse2net(s2)
    d = UpdateDiff.terms(sn1, sn2)
    assert d.added == {Term.create("D")}
    assert d.removed == {Term.create("A")}


def test_identify_changed_sentence() -> None:
    """変更前と変更後を同定したい."""
    s1 = """
        # title
            aaaaaold
            bbb
            ccc
            dsafdfewx
    """
    s2 = """
        # title
            bbb
            ccc
            aaaaanew
            ddd
    """

    sn1 = parse2net(s1)
    sn2 = parse2net(s2)
    assert identify_sentence(sn1, sn2) == {"aaaaaold": "aaaaanew"}


def test_identify_changed_term() -> None:
    """変更前と変更後を同定したい.

    条件
        同じ文(文の同定が先に必要かも)に紐付いている
        Term自体の類似 (共通aliasやnameを持つか).

        term,sentence
        変更あり,変更なし
        変更なし,変更あり


        変更あり,変更あり 同定必要

    """
    txt1 = """
        # title
            A: qawsedrftg
            PPP: aaa
            QQQ: zxcvbnm

    """

    txt2 = """
        # title
            A, B: qawsedrftg
            PPP: bbb
            RRR: zxcvbnmZ
    """
    sn1 = parse2net(txt1)
    sn2 = parse2net(txt2)
    assert identify_term(sn1, sn2) == {
        Term.create("A"): Term.create("A", "B"),
        Term.create("QQQ"): Term.create("RRR"),
    }


def test_edgediff() -> None:
    """関係の変更."""
    txt1 = """
        # title
            A: aaa
            B: bbb
            C: ccc
    """

    txt2 = """
        # title2
            A: aaa
                BB: bbb
            C: ccc
    """
    sn1 = parse2net(txt1)
    sn2 = parse2net(txt2)
    ed = create_edgediff(sn1, sn2)
    assert ed.removed == {
        EdgeType.SIBLING.to_tuple("aaa", "bbb"),
        EdgeType.SIBLING.to_tuple("bbb", "ccc"),
    }
    assert ed.added == {
        EdgeType.BELOW.to_tuple("aaa", "bbb"),
        EdgeType.SIBLING.to_tuple("aaa", "ccc"),
    }
