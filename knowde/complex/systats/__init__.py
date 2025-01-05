"""NW1 node0の値、統計値."""
from __future__ import annotations

import operator
from functools import reduce
from typing import Callable, Hashable, TypeAlias

import networkx as nx
from more_itertools import flatten

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import Duplicable
from knowde.complex.systats.nw1_n1 import (
    get_details,
    get_parent_or_none,
    has_dependency,
)
from knowde.primitive.term import Term

"""
node数
edge数
term数
sentences数
axioms数
字数
"""

Systats: TypeAlias = Callable[[SysNet], int]


def n_node(sn: SysNet) -> int:  # noqa: D103
    return len(sn.g.nodes)


def n_edge(sn: SysNet) -> int:  # noqa: D103
    return len(sn.g.edges)


def n_term(sn: SysNet) -> int:  # noqa: D103
    return len(sn.terms)


def n_sentence(sn: SysNet) -> int:  # noqa: D103
    return len(sn.sentences)


def n_char(sn: SysNet) -> int:  # noqa: D103
    c = 0
    for n in sn.g.nodes:
        match n:
            case str() | Duplicable():
                c += len(str(n))
            case Term():
                c += reduce(operator.add, map(len, n.names))
                c += len(n.alias) if n.alias else 0
            case _:
                raise TypeError
    return c


def n_isolation(_sn: SysNet) -> int:
    """孤立したnode."""


def get_isolation(sn: SysNet) -> list[Hashable]:
    """孤立したノード.

    SIBLINGは無視 <=> parentを持たない
    HEADも無視
    見出しとの関連も無視
    BELOW関係(詳細)を持たない
    TOを持たない
    """

    def include_isolation_node(n: Hashable) -> bool:
        """parentもなく、詳細もなく、TOなどの関係もない."""
        if n not in sn.sentences:
            return False
        parent = get_parent_or_none(sn, n)
        if parent is not None:
            return False
        details = list(flatten(get_details(sn, n)))
        if len(details) > 0:
            return False
        # d = sn.get(n)
        # if isinstance(d, Def):
        #     print("isinstance def::", n)
        #     print(sn.get_resolved(n))
        return not has_dependency(sn, n)

    sub = nx.subgraph_view(
        sn.g,
        filter_node=include_isolation_node,  # 見出し削除
    )
    return list(sub.nodes)


def n_axiom(_sn: SysNet) -> int:
    """出発点となるDef or sentence."""
    # axiom_paths()
    return 0
    # to_sub = filter_edge_attr(sn.g, "type", EdgeType.TO)
    # below_sub = filter_edge_attr(sn.g, "type", EdgeType.TO)
    # print(to_sub)
    # for _s in sn.sentences:
    #     pass
    # a_sibs = get_axioms(sn.g, EdgeType.BELOW)
    # parents = [(s, list(EdgeType.BELOW.pred(sn.g, s))) for s in a_sibs]
    # a = [p[0] for p in parents if p[1][0] in get_headings(sn.g, sn.root)]
    # print(a_sibs)

    # print(a)

    # def _f(u: Hashable, v: Hashable, attr: dict) -> bool:
    #     return g[u][v][attr]["type"] in types

    # sub: nx.MultiDiGraph = nx.subgraph_view(g, filter_edge=_f)


def get_systats(sn: SysNet) -> dict[str, int]:
    """系の統計情報."""
    # print(get_isolation(sn))
    return {
        "n_node": n_node(sn),
        "n_edge": n_edge(sn),
        "n_term": n_term(sn),
        "n_sentence": n_sentence(sn),
        "n_char": n_char(sn),
        "n_isolation": len(get_isolation(sn)),
    }
