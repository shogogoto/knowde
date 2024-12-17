"""test."""


import networkx as nx

from knowde.complex.system.sysnet import EdgeType

from . import Navi

"""
文同士のエッジを辿るのが基本

EdgeType毎に出発点は考えられるが、ここでは意味的なもの
    BELOW
        どのスコープなのか
    TO関係
        公理は何か
    RESOLVE
        最も素朴な概念は何か
statsでもaxiomは出せる
    あるnodeから遡るのではない
    isolate_node

paths

int
    依存元の数
    依存先の数
    axiom dist
    leaf dist
"""

# nx.lowest_common_ancestor()
# print(nx.number_of_nodes(sn.g))
# print(nx.number_of_edges(sn.g))
# print(nx.density(sn.g))


def test_navi() -> None:
    """ナビ."""
    # ╙── 0
    #     ├─╼ 1
    #     │   ├─╼ 3 - 99
    #     │   └─╼ 4
    #     └─╼ 2
    #         ├─╼ 5
    #         └─╼ 6 - 999
    g = nx.balanced_tree(2, 2, nx.DiGraph())
    g.add_edge(4, 99)
    g.add_edge(6, 999)
    nx.set_edge_attributes(g, EdgeType.TO, "type")
    navi = Navi.create(g, 0, EdgeType.TO)
    assert navi.succs(0) == [0]
    assert navi.succs(1) == [1, 2]
    assert navi.succs(2) == [3, 5, 4, 6]
    assert navi.succs(3) == [99, 999]
    assert navi.succs(-1) == [99, 999]
    assert navi.succs(999) == []


# def test_explorer() -> None:
#     """探索."""
#     navis = {}
#     for et in EdgeType:
#         print(type(et), str(et), et.name, et.value)
