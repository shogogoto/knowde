"""NW1 node0の値、統計値."""
from __future__ import annotations

import operator
from functools import reduce
from typing import Callable, Hashable, TypeAlias

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import Duplicable
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


def get_isolation(sn: SysNet) -> None:
    """孤立したノード.

    SIBLINGは無視 <=> parentを持たない
    HEADも無視
    見出しとの関連も無視
    BELOW関係(詳細)を持たない
    TOを持たない
    """

    def include_isolation_edge(u: Hashable, v: Hashable, idx: int) -> bool:
        """parentもなく、詳細もなく、TOなどの関係もない."""
        _et = sn.g[u][v][idx]
        # print(u, v, et)
        # filter_edge=lambda u, v, attr: sn.g[u][v][attr]["type"] != EdgeType.HEAD,
        return False

    # sub = nx.subgraph_view(
    #     sn.g,
    #     filter_node=lambda n: n in sn.sentences,  # 見出し削除
    #     filter_edge=include_isolation_edge,
    # )

    # print("#" * 80)
    # nxprint(sub)
    # print(sub.nodes)
    # print(sub.edges)


def n_axiom(_sn: SysNet) -> int:
    """出発点となるDef or sentence."""
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
    return {
        "n_node": n_node(sn),
        "n_edge": n_edge(sn),
        "n_term": n_term(sn),
        "n_sentence": n_sentence(sn),
        "n_char": n_char(sn),
    }
