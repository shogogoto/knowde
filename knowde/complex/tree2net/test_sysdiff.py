"""系の差分."""


from knowde.complex.system.sysdiff import (
    SysNodeDiff,
    identify_sentence,
    identify_term,
)
from knowde.complex.tree2net import parse2net
from knowde.primitive.term import Term


def test_term_diff() -> None:
    """用語差分."""
    _s1 = """
        # title
            A: a
            B: b
            c
    """
    _s2 = """
        # title
            B: b
            c
            D: d
    """

    sn1 = parse2net(_s1)
    sn2 = parse2net(_s2)
    d = SysNodeDiff.terms(sn1, sn2)
    assert d.added == {Term.create("D")}
    assert d.removed == {Term.create("A")}


def test_identify_changed_sentence() -> None:
    """変更前と変更後を同定したい."""
    _s1 = """
        # title
            aaaaaold
            bbb
            ccc
            dsafdfewx
    """
    _s2 = """
        # title
            bbb
            ccc
            aaaaanew
            ddd
    """

    sn1 = parse2net(_s1)
    sn2 = parse2net(_s2)
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
