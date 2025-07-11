"""test.

誰でも見れる


register user
knowde search


sync
"""

import networkx as nx
from neomodel import db
from pytest_unordered import unordered

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.knowde.repo import (
    save_text,
    search_knowde,
)
from knowde.feature.knowde.repo.cypher import q_stats
from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.stats.nxdb.restore import restore_sysnet
from knowde.feature.stats.nxdb.save import sn2db
from knowde.shared.labels.user import LUser
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.types import UUIDy, to_uuid

from .clause import OrderBy, Paging, WherePhrase


@async_fixture()
async def u() -> LUser:  # noqa: D103
    return await LUser(email="onex@gmail.com").save()


@mark_async_test()
async def test_search_knowde_by_txt(u: LUser):
    """文の所属などを取得."""
    s = """
    # titleX
    ## h11
        A, A1, A2: a
            when. 20C
            <- premise1
            <- premise2
            -> P: aaa
                -> leaf
            aaaa
        B: bA123
        A11, TNTN: ちん
        D: bbbaaaaa
    ## h12
        x: xxx
        y: {x}yy
    """
    _sn, _ = await save_text(u.uid, s)
    _total, adjs = search_knowde("A1")
    assert [a.center.sentence for a in adjs] == unordered(["a", "ちん", "bA123"])

    _total, adjs = search_knowde("xxx")
    assert adjs[0].referreds[0].sentence == "{x}yy"


def get_stats_by_id(uid: UUIDy) -> list[int] | None:
    """systats相当のものをDBから取得する(動作確認用)."""
    q = rf"""
        CALL () {{

        MATCH (tgt:Sentence) WHERE tgt.uid= $uid
        {q_stats("tgt")}
        }}
        WITH stats AS st
        RETURN
            st.n_premise
            , st.n_conclusion
            , st.dist_axiom
            , st.dist_leaf
            , st.n_referred
            , st.n_refer
            , st.n_detail
    """
    res = db.cypher_query(
        q,
        params={"uid": to_uuid(uid).hex},
        resolve_objects=True,
    )
    return res[0][0] if res else None


@mark_async_test()
async def test_stats_from_db(u: LUser):
    """systats相当のものをDBから取得する."""
    s = """
    # titleX
        0
            <- -1
                <- -11
                <- -12
            <- -2
                <- -21
                <- -22
            -> 1
                -> 11
                -> 12
            -> 2
                -> 21
                -> 22
                    -> 221
        A: a
        B: b{A}b
        C: c{B}c
            -> ccc
        detail
            d1
            d2
            d3
                d31
                d32
    """
    _, r = await save_text(u.uid, s)
    _sn, uids = await restore_sysnet(r.uid)
    assert get_stats_by_id(uids["0"]) == [6, 7, 2, 3, 0, 0, 0]
    assert get_stats_by_id(uids["1"]) == [7, 2, 3, 1, 0, 0, 0]
    assert get_stats_by_id(uids["a"]) == [0, 0, 0, 0, 2, 0, 0]
    assert get_stats_by_id(uids["b{A}b"]) == [0, 0, 0, 0, 1, 1, 0]
    assert get_stats_by_id(uids["detail"]) == [0, 0, 0, 0, 0, 0, 5]


@mark_async_test()
async def test_paging(u: LUser):
    """ページングのテスト."""
    sn, r = await save_text(u.uid, "# titleY\n")
    g = nx.balanced_tree(3, 4, create_using=nx.MultiDiGraph)
    g = nx.relabel_nodes(g, {i: str(i) for i in g.nodes})
    nx.set_edge_attributes(g, EdgeType.TO, "type")
    h = nx.compose(sn.g, g)
    EdgeType.BELOW.add_edge(h, sn.root, "0")
    sn = SysNet(root=sn.root, g=h)
    sn2db(sn, r.uid)
    sn, _uids = await restore_sysnet(r.uid)
    n_nodes = len(sn.g.nodes) - 1
    assert n_nodes == 121  # title除いて121の文  # noqa: PLR2004
    total, adjs = search_knowde(".*", WherePhrase.REGEX, Paging(page=1))
    assert total == n_nodes
    assert len(adjs) == 100  # noqa: PLR2004

    total, adjs = search_knowde(".*", WherePhrase.REGEX, Paging(page=2))
    assert len(adjs) == 21  # noqa: PLR2004

    total, adjs = search_knowde(".*", WherePhrase.REGEX, Paging(page=3))
    assert len(adjs) == 0


@mark_async_test()
async def test_ordering(u: LUser):
    """検索結果の順番を確認.

    sortをどう生成するのか
    scoreの定義 weight * var の sumというのだけでいい
    desc asc
    """
    sn, r = await save_text(u.uid, "# titleY\n")
    g = nx.path_graph(30, create_using=nx.MultiDiGraph)
    g = nx.relabel_nodes(g, {i: str(i) for i in g.nodes})
    nx.set_edge_attributes(g, EdgeType.TO, "type")
    h = nx.compose(sn.g, g)
    EdgeType.BELOW.add_edge(h, sn.root, "0")
    sn = SysNet(root=sn.root, g=h)
    sn2db(sn, r.uid)
    sn, _uids = await restore_sysnet(r.uid)
    order_by = OrderBy(
        n_detail=0,
        n_premise=-1,
        n_conclusion=0,
        n_refer=0,
        n_referred=-0,
        dist_axiom=0,
        dist_leaf=0,
    )
    _total, adjs = search_knowde(
        ".*",
        WherePhrase.REGEX,
        order_by=order_by,
    )
    assert [a.center.sentence for a in adjs] == [str(i) for i in range(30)]


@mark_async_test()
async def test_details(u: LUser):
    """詳細の取得が変だったから."""
    s = """
    # titleX
        detail1
            d1
                when. 114
                d11
                d12
            d2
            d3
                d31
                d32
                    d33
        detail2
            x1
            X2: x2
            X3, X31: x3
                when. 514
                x4
                    x5
                    x6

    """
    _, r = await save_text(u.uid, s)
    _sn, _uids = await restore_sysnet(r.uid)
    _total, adjs = search_knowde(
        "detail",
        WherePhrase.CONTAINS,
        # do_print=True,
    )

    assert [str(k) for k in adjs[0].details] == ["d1T(114)", "d2", "d3"]
    assert [str(k) for k in adjs[1].details] == ["x1", "x2[X2]", "x3[X3(X31)]T(514)"]
    # 旧nameクエリでは x2[X2] が取得できなかった x2 だけで名前取得できなかった
