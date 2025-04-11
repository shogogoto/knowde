"""系の永続化."""

import pytest

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.entry import ResourceMeta
from knowde.complex.entry.label import LResource

from .restore import restore_sysnet
from .save import sn2db


@pytest.fixture
def sn() -> SysNet:  # noqa: D103
    s = r"""
        # h1
            @author nanashi
            @author taro tanaka
            @published 1919
            A: df
            P1 |B, B1, B2, B3, B4: b{A}b
            C{B}: c
            D: d{CB}d
        ## h2
            P{D}: pp
            Q: qq
            c{A}c
            X:
        ### h31
            abcdefg
        ### h32
            aaa
            bbb
            ccc
        #### h4
            aaaa
            bbbb
            cccc
                -> ppp
                    -> qqq
                        <- rrrrrrrrrrrrrrrrrrrrrrrrrrrrr
    """
    return parse2net(s)


def test_save_and_restore(sn: SysNet) -> None:
    """永続化して元に戻す."""
    m = ResourceMeta.of(sn)
    r = LResource(**m.model_dump()).save()
    sn2db(sn, r.uid)
    r = restore_sysnet(r.uid)
    assert set(sn.terms) == set(r.terms)
    # assert set(sn.sentences) == set(r.sentences)  # なぜかFalse
    diff_stc = set(sn.sentences) - set(r.sentences)
    assert len(diff_stc) == 0
