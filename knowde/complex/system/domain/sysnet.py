"""系ネットワーク."""
from __future__ import annotations

from enum import Enum, auto
from functools import cached_property
from itertools import chain, pairwise
from typing import Any, Hashable

import networkx as nx
from networkx import DiGraph
from pydantic import BaseModel, Field

from knowde.complex.system.domain.nxutil import succ_attr, to_nodes
from knowde.complex.system.domain.sysnode import Def, SysNodeType
from knowde.core.types import NXGraph

from .term.domain import MergedTerms, Term, TermResolver


class EdgeType(Enum):
    """グラフ関係の種類."""

    HEAD = auto()  # 見出しを配下にする
    SIBLING = auto()  # 兄弟 同階層 並列
    BELOW = auto()  # 配下 階層が下がる 直列
    DEF = auto()  # term -> 文
    RESOLVE = auto()  # 用語解決関係

    TO = auto()  # 依存
    CONCRETE = auto()  # 具体
    WHEN = auto()
    # 両方向
    ANTI = auto()  # 反対

    def add_edge(self, g: nx.DiGraph, pre: Hashable, suc: Hashable) -> None:
        """エッジ追加."""
        g.add_edge(pre, suc, type=self)
        # if self == EdgeType.ANTI:
        #     g.add_edge(suc, pre, type=self)


class Heading(BaseModel):
    """見出しへの簡単追加用."""

    v: str
    g: NXGraph = Field(default_factory=DiGraph, init=False)


class SystemNetwork(BaseModel):
    """系ネットワーク."""

    root: str
    g: NXGraph = Field(default_factory=DiGraph, init=False)

    def model_post_init(self, __context: Any) -> None:  # noqa: ANN401 D102
        self.g.add_node(self.root)

    # 見出しだけstr限定だからtype hint用にメソッドを用意した
    def head(self, pre: str, succ: str) -> None:
        """見出し追加."""
        EdgeType.HEAD.add_edge(self.g, pre, succ)

    def add(self, t: EdgeType, *path: SysNodeType) -> None:
        """既存nodeから開始していない場合はrootからedgeを伸ばすように登録."""
        niter = iter(path)
        try:
            first = next(niter)
        except StopIteration:
            return
        first = (self.root, first) if first not in self.g else (first,)
        for pre, suc in pairwise(chain(first, niter)):
            p = self._add(pre)
            s = self._add(suc)
            t.add_edge(self.g, p, s)

    def _add(self, n: SysNodeType) -> str | Term:
        """定義の追加."""
        match n:
            case Term() | str():
                self.g.add_node(n)
                return n
            case Def():
                EdgeType.DEF.add_edge(self.g, n.term, n.sentence)
                return n.sentence
            case _:
                raise TypeError

    @cached_property
    def resolver(self) -> TermResolver:
        """用語解決器."""
        mt = MergedTerms(terms=[n for n in self.g.nodes if isinstance(n, Term)])
        return mt.to_resolver()


class HeadingNotFoundError(Exception):
    """見出しが見つからない."""


def get_headings(sn: SystemNetwork) -> set[Hashable]:
    """見出し一覧."""
    return to_nodes(sn.g, sn.root, succ_attr("type", EdgeType.HEAD))


def heading_path(sn: SystemNetwork, n: Hashable) -> list[Hashable]:
    """直近の見出しパス."""
    paths = list(nx.shortest_simple_paths(sn.g, sn.root, n))
    if len(paths) == 0:
        raise HeadingNotFoundError
    p = paths[0]
    return [e for e in p if e in get_headings(sn)]
