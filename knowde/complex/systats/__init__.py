"""NW1 node0の値、統計値."""
from __future__ import annotations

import operator
from enum import Enum
from functools import cache, reduce
from typing import Callable, Hashable, TypeAlias

import networkx as nx

from knowde.complex.__core__.sysnet import SysNet
from knowde.complex.__core__.sysnet.sysnode import Duplicable, SysArg
from knowde.complex.systats.nw1_n1 import (
    get_detail,
    get_parent_or_none,
    has_dependency,
)
from knowde.primitive.__core__.nxutil.edge_type import EdgeType, etype_subgraph
from knowde.primitive.term import Term

SystatsFn: TypeAlias = Callable[[SysNet], int]
SystatsRatioFn: TypeAlias = Callable[[SysNet], float]


class Systats(Enum):
    """統計情報の構成要素."""

    EDGE = ("edge", lambda sn: len(sn.g.edges))
    TERM = ("term", lambda sn: len(sn.terms))
    SENTENCE = ("sentence", lambda sn: len(sn.sentences))
    CHAR = ("char", lambda sn: n_char(sn))
    ISOLATION = ("isolation", lambda sn: len(get_isolation(sn)))
    AXIOM = ("axiom", lambda sn: len(get_axiom_to(sn)))
    TERM_AXIOM = ("term_axiom", lambda sn: len(get_axiom_resolved(sn)))

    label: str
    fn: SystatsFn

    def __init__(self, label: str, fn: SystatsFn) -> None:
        """For merge."""
        self.label = label
        self.fn = fn


class UnificationRatio(Enum):
    """1系の統合化(まとまり具体)指標.

    Systatsの組み合わせ
    """

    # 時間かかりすぎ
    ISOLATION = (
        "isoration_ratio",
        lambda sn: Systats.ISOLATION.fn(sn) / Systats.SENTENCE.fn(sn),
    )
    TERM = (
        "axiom_term_ratio",
        lambda sn: Systats.TERM_AXIOM.fn(sn) / Systats.TERM.fn(sn),
    )
    AXIOM = (
        "axiom_ratio",
        lambda sn: Systats.AXIOM.fn(sn) / Systats.SENTENCE.fn(sn),
    )

    label: str
    fn: SystatsRatioFn

    def __init__(self, label: str, fn: SystatsRatioFn) -> None:
        """For merge."""
        self.label = label
        self.fn = lambda sn: round(fn(sn), 3)


def n_char(sn: SysNet) -> int:  # noqa: D103
    c = 0
    for n in sn.g.nodes:
        match n:
            case str() | Duplicable():
                c += len(str(n))
            case Term():
                c += 0 if len(n.names) == 0 else reduce(operator.add, map(len, n.names))
                c += len(n.alias) if n.alias else 0
            case _:
                raise TypeError
    return c


@cache
def get_isolation(sn: SysNet) -> list[Hashable]:
    """孤立したノード.

    SIBLINGは無視 <=> parentを持たない
    HEAD、TO、RESOLVEDも無視
    """

    def include_isolation_node(n: Hashable) -> bool:
        """parentもなく、詳細もなく、TOなどの関係もない."""
        parent = get_parent_or_none(sn, n)
        if parent is not None:
            return False
        if has_dependency(sn, n):
            return False
        detail = get_detail(sn, n)
        return len(detail) == 0

    sub = etype_subgraph(sn.sentence_graph, EdgeType.SIBLING, EdgeType.BELOW)
    sub = nx.subgraph_view(
        sub,
        filter_node=include_isolation_node,  # 見出し削除
    )
    return list(sub.nodes)


@cache
def get_axiom_to(sn: SysNet) -> list[Hashable]:
    """TOの出発点となるDef or sentence."""

    def filter_axiom(n: Hashable) -> bool:
        has_to = len(list(EdgeType.TO.succ(sn.g, n))) > 0
        has_from = len(list(EdgeType.TO.pred(sn.g, n))) == 0
        return has_to and has_from

    sub = nx.subgraph_view(
        etype_subgraph(sn.sentence_graph, EdgeType.TO),
        filter_node=filter_axiom,  # 見出し削除
    )
    return list(sub.nodes)


@cache
def get_axiom_resolved(sn: SysNet) -> list[SysArg]:
    """RESOLVEDの出発点."""

    def filter_axiom(n: Hashable) -> bool:
        has_refer = len(list(EdgeType.RESOLVED.pred(sn.g, n))) > 0
        has_referred = len(list(EdgeType.RESOLVED.succ(sn.g, n))) == 0
        return has_refer and has_referred

    sub = nx.subgraph_view(
        etype_subgraph(sn.sentence_graph, EdgeType.RESOLVED),
        filter_node=filter_axiom,  # 見出し削除
    )
    return list(sub.nodes)
