"""test."""

import networkx as nx

from knowde.complex.system.domain.nxutil import nxconvert, nxprint

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
    g = nx.balanced_tree(2, 3, nx.DiGraph())
    g = nxconvert(g, str)
    nxprint(g)
