"""domain."""

import operator
from collections.abc import Hashable
from functools import cache, reduce
from typing import Self

import networkx as nx
from pydantic import BaseModel, Field, computed_field

from knowde.feature.parsing.primitive.term import Term
from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.sysnet.sysnode import KNArg
from knowde.feature.stats.systats.nw1_n1 import (
    get_detail,
    get_parent_or_none,
    has_dependency,
)
from knowde.shared.nxutil.edge_type import EdgeType, etype_subgraph, is_leaf, is_root
from knowde.shared.types import Duplicable


class ResourceStatsStd(BaseModel):
    """基本リソース統計情報."""

    n_char: int = Field(title="文字数")
    n_sentence: int = Field(title="単文数")
    n_term: int = Field(title="単語数")
    n_edges: int = Field(title="辺数")

    n_isolation: int = Field(title="孤立単文数")
    n_axiom: int = Field(title="公理数")
    n_unrefered: int = Field(title="未参照数")

    @computed_field
    @property
    def r_isolation(self) -> float:
        """孤立割合. 低いほどネットワークのまとまりが良い."""
        if self.n_sentence == 0:
            return 0.0
        return self.n_isolation / self.n_sentence

    @computed_field
    @property
    def r_axiom(self) -> float:
        """全単文に対する公理割合.

        公理割合が低いほどまとまりが良い. オッカムの剃刀的な
        """
        if self.n_sentence == 0:
            return 0.0
        return self.n_axiom / self.n_sentence

    @computed_field
    @property
    def r_unrefered(self) -> float:
        """全用語の未参照語割合.

        未参照語割合が少ないほど「浮いた用語」がなくまとまりが良い.
        """
        if self.n_term == 0:
            return 0.0
        return self.n_unrefered / self.n_term

    @classmethod
    def create(cls, sn: SysNet) -> Self:  # noqa: D102
        def n_char(sn: SysNet) -> int:
            c = 0
            for n in sn.g.nodes:
                match n:
                    case str() | Duplicable():
                        c += len(str(n))
                    case Term():
                        c += (
                            0
                            if len(n.names) == 0
                            else reduce(operator.add, map(len, n.names))
                        )
                        c += len(n.alias) if n.alias else 0
                    case _:
                        raise TypeError
            return c

        return cls(
            n_char=n_char(sn),
            n_sentence=len(sn.sentences),
            n_term=len(sn.terms),
            n_edges=len(sn.g.edges),
            n_isolation=len(get_isolation(sn)),
            n_axiom=len(get_axiom(sn)),
            n_unrefered=len(get_unrefered(sn)),
        )


class ResourceStatsHeavy(BaseModel):
    """グラフ理論の指標 計算重い."""

    # diameter: float = Field(title="直径")
    # radius: float = Field(title="半径")
    density: float = Field(title="密度")

    @classmethod
    def create(cls, sn: SysNet) -> Self:  # noqa: D102
        return cls(
            # diameter=nx.diameter(sn.g),
            # radius=nx.radius(sn.g),
            density=nx.density(sn.g),
        )


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

    # まず detail方向で絞る
    sub = etype_subgraph(sn.sentence_graph, EdgeType.SIBLING, EdgeType.BELOW)
    sub = nx.subgraph_view(
        sub,
        filter_node=include_isolation_node,
    )
    return list(sub.nodes)


@cache
def get_axiom(sn: SysNet) -> list[Hashable]:
    """TOの出発点となるDef or sentence."""
    sub = nx.subgraph_view(
        etype_subgraph(sn.sentence_graph, EdgeType.TO),
        filter_node=lambda n: is_root(sn.g, n, EdgeType.TO),
    )
    return list(sub.nodes)


@cache
def get_unrefered(sn: SysNet) -> list[KNArg]:
    """RESOLVEDの出発点.

    公理に対応する出発点となる用語を無定義用語 undefined term
    これになぞらえた命名
    """
    sub = nx.subgraph_view(
        etype_subgraph(sn.sentence_graph, EdgeType.RESOLVED),
        filter_node=lambda n: is_leaf(sn.g, n, EdgeType.RESOLVED),  # 見出し削除
    )
    return list(sub.nodes)
