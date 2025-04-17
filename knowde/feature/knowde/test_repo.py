"""test.

誰でも見れる


register user
knowde search


sync
"""

import networkx as nx
import pytest
from pytest_unordered import unordered

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.nxdb.restore import restore_sysnet
from knowde.complex.nxdb.save import sn2db
from knowde.feature.knowde import KStats
from knowde.feature.knowde.cypher import OrderBy, Paging, WherePhrase
from knowde.feature.knowde.repo import get_stats_by_id, save_text, search_knowde
from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.user.repo import LUser


@pytest.fixture
def u() -> LUser:  # noqa: D103
    return LUser(email="onex@gmail.com").save()


def test_get_knowde_attrs(u: LUser):
    """文の所属などを取得."""
    s = """
    # titleX
        @author John Due
        @published H20/11/1
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
    _sn, _ = save_text(u.uid, s)
    adjs = search_knowde("A1")
    assert [a.center.sentence for a in adjs] == unordered(["a", "ちん", "bA123"])

    adjs = search_knowde("xxx")
    assert adjs[0].referreds[0].sentence == "{x}yy"


def test_stats_from_db(u: LUser):
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
    _, r = save_text(u.uid, s)
    _sn, uids = restore_sysnet(r.uid)
    assert get_stats_by_id(uids["0"]) == [6, 7, 2, 3, 0, 0, 0]
    assert get_stats_by_id(uids["1"]) == [7, 2, 3, 1, 0, 0, 0]
    assert get_stats_by_id(uids["a"]) == [0, 0, 0, 0, 2, 0, 0]
    assert get_stats_by_id(uids["b{A}b"]) == [0, 0, 0, 0, 1, 1, 0]
    assert get_stats_by_id(uids["detail"]) == [0, 0, 0, 0, 0, 0, 5]


def test_paging(u: LUser):
    """ページングのテスト."""
    sn, r = save_text(u.uid, "# titleY\n")
    g = nx.balanced_tree(3, 4, create_using=nx.MultiDiGraph)
    g = nx.relabel_nodes(g, {i: str(i) for i in g.nodes})
    nx.set_edge_attributes(g, EdgeType.TO, "type")
    h = nx.compose(sn.g, g)
    EdgeType.BELOW.add_edge(h, sn.root, "0")
    sn = SysNet(root=sn.root, g=h)
    sn2db(sn, r.uid)
    sn, _uids = restore_sysnet(r.uid)
    assert len(sn.g.nodes) == 122  # title除いて121の文  # noqa: PLR2004
    adjs = search_knowde(".*", WherePhrase.REGEX, Paging(page=1))
    assert len(adjs) == 100  # noqa: PLR2004
    adjs = search_knowde(".*", WherePhrase.REGEX, Paging(page=2))
    assert len(adjs) == 21  # noqa: PLR2004
    adjs = search_knowde(".*", WherePhrase.REGEX, Paging(page=3))
    assert len(adjs) == 0


def test_ordering(u: LUser):
    """検索結果の順番を確認.

    sortをどう生成するのか
    scoreの定義 weight * var の sumというのだけでいい
    desc asc
    """
    sn, r = save_text(u.uid, "# titleY\n")
    g = nx.path_graph(30, create_using=nx.MultiDiGraph)
    g = nx.relabel_nodes(g, {i: str(i) for i in g.nodes})
    nx.set_edge_attributes(g, EdgeType.TO, "type")
    h = nx.compose(sn.g, g)
    EdgeType.BELOW.add_edge(h, sn.root, "0")
    sn = SysNet(root=sn.root, g=h)
    sn2db(sn, r.uid)
    sn, _uids = restore_sysnet(r.uid)
    order_by = OrderBy(
        weight=KStats(
            n_detail=0,
            n_premise=-1,
            n_conclusion=0,
            n_refer=0,
            n_referred=-0,
            dist_axiom=0,
            dist_leaf=0,
        ),
    )
    adjs = search_knowde(
        ".*",
        WherePhrase.REGEX,
        order_by=order_by,
    )
    assert [a.center.sentence for a in adjs] == [str(i) for i in range(30)]
