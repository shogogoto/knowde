"""NW1 node0の値、統計値."""
from __future__ import annotations

import operator
from functools import reduce
from typing import Callable, Hashable, TypeAlias

import networkx as nx
from more_itertools import flatten

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import Duplicable, SysArg
from knowde.complex.systats.nw1_n1 import (
    get_details,
    get_parent_or_none,
    has_dependency,
)
from knowde.primitive.__core__.nxutil.edge_type import EdgeType
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
        return not has_dependency(sn, n)

    sub = nx.subgraph_view(
        sn.g,
        filter_node=include_isolation_node,  # 見出し削除
    )
    return list(sub.nodes)


def get_axiom_to(sn: SysNet) -> list[Hashable]:
    """TOの出発点となるDef or sentence."""

    def filter_axiom(n: Hashable) -> bool:
        """parentもなく、詳細もなく、TOなどの関係もない."""
        if n not in sn.sentences:
            return False
        has_to = len(list(EdgeType.TO.succ(sn.g, n))) > 0
        has_from = len(list(EdgeType.TO.pred(sn.g, n))) == 0
        return has_to and has_from

    sub = nx.subgraph_view(
        sn.g,
        filter_node=filter_axiom,  # 見出し削除
    )
    return list(sub.nodes)


def get_axiom_resolved(sn: SysNet) -> list[SysArg]:
    """RESOVEDの出発点."""

    def filter_axiom(n: Hashable) -> bool:
        """parentもなく、詳細もなく、TOなどの関係もない."""
        if n not in sn.sentences:
            return False
        has_refer = len(list(EdgeType.RESOLVED.pred(sn.g, n))) > 0
        has_referred = len(list(EdgeType.RESOLVED.succ(sn.g, n))) == 0
        return has_refer and has_referred

    sub = nx.subgraph_view(
        sn.g,
        filter_node=filter_axiom,  # 見出し削除
    )
    return [sn.get(n) for n in sub.nodes]


def get_systats(sn: SysNet) -> dict[str, int]:
    """系の統計情報."""
    return {
        "n_edge": n_edge(sn),
        "n_term": n_term(sn),
        "n_sentence": n_sentence(sn),
        "n_char": n_char(sn),
        "n_isolation": len(get_isolation(sn)),
    }
