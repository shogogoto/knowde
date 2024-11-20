"""系ネットワーク."""
from __future__ import annotations

from enum import Enum, auto
from functools import cached_property
from itertools import chain, pairwise
from typing import Any, Hashable

import networkx as nx
from networkx import DiGraph
from pydantic import BaseModel, Field, PrivateAttr

from knowde.complex.system.domain.nxutil import (
    Accessor,
    pred_attr,
    succ_attr,
    to_nested,
    to_nodes,
)
from knowde.core.types import NXGraph
from knowde.primitive.term import MergedTerms, Term, TermResolver

from .errors import UnResolvedTermError
from .sysnode import Def, SysNodeType


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
    _is_resolved: bool = PrivateAttr(default=False)

    def model_post_init(self, __context: Any) -> None:  # noqa: ANN401 D102
        self.g.add_node(self.root)

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
    def headings(self) -> set[str]:
        """見出しセット."""
        ns = to_nodes(self.g, self.root, succ_attr("type", EdgeType.HEAD))
        return {str(n) for n in ns}

    @property
    def sentences(self) -> list[str]:
        """文."""
        s = [n for n in self.g.nodes if isinstance(n, str)]
        [s.remove(h) for h in self.headings]
        return s

    @property
    def resolver(self) -> TermResolver:
        """用語解決器."""
        return (
            MergedTerms()
            .add(
                *[n for n in self.g.nodes if isinstance(n, Term)],
            )
            .to_resolver()
        )

    def setup_resolver(self) -> None:
        """事前の全用語解決.

        統計情報を得るためには、全て用語解決しとかないといけない
        DBやstageからは解決済みのnetworkを復元
        """
        r = self.resolver
        for s in self.sentences:
            d = r(s)
            td = r.mark2term(d)
            _add_resolve_edge(self, s, td)
        self._is_resolved = True

    def get_resolved(self, s: str) -> dict:
        """解決済み入れ子文を取得."""
        if not self._is_resolved:
            raise UnResolvedTermError
        return to_nested(self.g, s, EdgeType.RESOLVE.succ)


def _add_resolve_edge(sn: SystemNetwork, start: str, termd: dict) -> None:
    """(start)-[RESOLVE]->(marked sentence)."""
    for k, v in termd.items():
        s = next(EdgeType.DEF.succ(sn.g, k))  # 文
        EdgeType.RESOLVE.add_edge(sn.g, start, s)  # 文 -> 文
        if any(v):  # 空でない
            _add_resolve_edge(sn, str(s), v)


def isolate_node(_sn: SystemNetwork) -> None:
    """孤立したノード."""
