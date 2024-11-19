"""系ネットワーク."""
from __future__ import annotations

from enum import Enum, auto
from functools import cached_property
from itertools import chain, pairwise
from typing import Any, Hashable

import networkx as nx
from networkx import DiGraph
from pydantic import BaseModel, Field

from knowde.complex.system.domain.errors import HeadingNotFoundError
from knowde.complex.system.domain.nxutil import (
    Accessor,
    pred_attr,
    succ_attr,
    to_nested,
    to_nodes,
)
from knowde.complex.system.domain.sysnode import Def, SysNodeType
from knowde.core.types import NXGraph

from .term import MergedTerms, Term, TermResolver


class EdgeType(Enum):
    """グラフ関係の種類."""

    HEAD = auto()  # 見出しを配下にする
    SIBLING = auto()  # 兄弟 同階層 並列
    BELOW = auto()  # 配下 階層が下がる 直列
    DEF = auto()  # term -> 文
    RESOLVE = auto()  # 用語解決関係 文 -> 文

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

    @cached_property
    def succ(self) -> Accessor:
        """エッジを辿って次を取得."""
        return succ_attr("type", self)

    @cached_property
    def pred(self) -> Accessor:
        """エッジを遡って前を取得."""
        return pred_attr("type", self)


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

    def add(self, t: EdgeType, *path: SysNodeType) -> tuple[SysNodeType, ...]:
        """既存nodeから開始していない場合はrootからedgeを伸ばすように登録."""
        niter = iter(path)
        try:
            first = next(niter)
        except StopIteration:
            return path
        first = (self.root, first) if first not in self.g else (first,)
        for pre, suc in pairwise(chain(first, niter)):
            p = self._add(pre)
            s = self._add(suc)
            t.add_edge(self.g, p, s)
        return path

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

    @property
    def resolver(self) -> TermResolver:
        """用語解決器."""
        return (
            MergedTerms()
            .add(*[n for n in self.g.nodes if isinstance(n, Term)])
            .to_resolver()
        )

    @property
    def sentences(self) -> list[str]:
        """文."""
        s = [n for n in self.g.nodes if isinstance(n, str)]
        [s.remove(str(h)) for h in get_headings(self)]
        return s


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


def setup_resolver(sn: SystemNetwork) -> None:
    """事前の全用語解決.

    統計情報を得るためには、全て用語解決しとかないといけない
    DBやstageからは解決済みのnetworkを復元
    """
    r = sn.resolver
    for s in sn.sentences:
        d = r(s)
        td = r.mark2term(d)
        add_resolve_edge(sn, s, td)


def add_resolve_edge(sn: SystemNetwork, start: str, termd: dict) -> None:
    """(start)-[RESOLVE]->(marked sentence)."""
    for k, v in termd.items():
        s = next(EdgeType.DEF.succ(sn.g, k))  # 文
        EdgeType.RESOLVE.add_edge(sn.g, start, s)  # 文 -> 文
        if any(v):  # 空でない
            add_resolve_edge(sn, str(s), v)


def get_resolved(sn: SystemNetwork, s: str) -> dict:
    """解決済み入れ子文を取得."""
    return to_nested(sn.g, s, EdgeType.RESOLVE.succ)


def isolate_node(_sn: SystemNetwork) -> None:
    """孤立したノード."""
