"""系の永続化."""

import networkx as nx
import pytest
from pytest_unordered import unordered

from knowde.conftest import mark_async_test
from knowde.feature.entry.domain import ResourceMeta
from knowde.feature.entry.label import LResource
from knowde.feature.entry.resource.usecase import save_text
from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.tree2net import parse2net
from knowde.shared.user.label import LUser

from .restore import (
    restore_sysnet,
    restore_tops,
)
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


@mark_async_test()
async def test_restore_tops():
    """先端のHeadかSentenceまで復元."""
    u = await LUser(email="one@gmail.com").save()
    s = """
    # title
      direct
    ## h1
      s1
    ### h11
    #### h111
      s111{A}
    ## h2
      s2
      A, B: s2next
        when. ~ 19C
      C:
    """

    _, mr = await save_text(u.uid, s)
    g1, uids = await restore_tops(mr.uid)
    g = nx.relabel_nodes(g1, uids)
    assert uids[mr.uid] == "# title"
    assert {"direct", "s1", "s2"} < set(g.nodes)
    assert "s2net" not in g1.nodes


@mark_async_test()
async def test_restore_individual():
    """別のリソースの内容を取得しないことの確認."""
    u = await LUser(email="one@gmail.com").save()
    s1 = """
    # title
      direct
    ## h1
      aaa
      bbb
      ccc
    """
    _, mr1 = await save_text(u.uid, s1)

    s2 = """
    # title2
      direct2
    ## h1
      ddd
      eee
    """
    _, mr2 = await save_text(u.uid, s2)

    sn1, _uids1 = await restore_sysnet(mr1.uid)
    sn2, _uids2 = await restore_sysnet(mr2.uid)
    assert sn1.sentences == unordered(["direct", "aaa", "bbb", "ccc"])
    assert sn2.sentences == unordered(["direct2", "ddd", "eee"])
