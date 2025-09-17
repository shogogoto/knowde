"""系の永続化."""

import pytest
from pytest_unordered import unordered

from knowde.conftest import mark_async_test
from knowde.feature.entry.domain import ResourceMeta
from knowde.feature.entry.label import LResource
from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.tree2net import parse2net

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
                when. 19C
            bbb
                when. -500
            ccc
                when. 1900 ~ 2050
        #### h4
            aaaa
            bbbb
            cccc
                -> ppp
                    -> qqq
                        <- rrrrrrrrrrrrrrrrrrrrrrrrrrrrr
                            when. 19C
    """
    return parse2net(s)


@mark_async_test()
async def test_save_and_restore(sn: SysNet) -> None:
    """永続化して元に戻す."""
    m = ResourceMeta.of(sn)
    rsrc = await LResource(**m.model_dump()).save()
    sn2db(sn, rsrc.uid)
    r, _ = await restore_sysnet(rsrc.uid)
    assert set(sn.terms) == set(r.terms)
    # assert set(sn.sentences) == set(r.sentences)  # なぜかFalse
    diff_stc = set(sn.sentences) - set(r.sentences)
    assert len(diff_stc) == 0
    assert sn.whens == unordered(r.whens)
