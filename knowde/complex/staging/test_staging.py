"""test staging."""

import networkx as nx

from knowde.feature.parsing.file_io import nx2json_dump, nxread
from knowde.feature.parsing.tree2net import parse2net


def test_inout() -> None:
    """In out is equal."""
    s1 = r"""
        # h1
            a
            b
            c
                -> d
                e
                f
                    <- `X`
        ## h2
            X: x
            Y: y
            +++ zzz +++
            W:
    """
    sn = parse2net(s1)
    js = nx2json_dump(sn.g)
    g = nxread(js)

    assert nx.is_isomorphic(sn.g, g)
    assert nx.graph_edit_distance(sn.g, g) == 0
