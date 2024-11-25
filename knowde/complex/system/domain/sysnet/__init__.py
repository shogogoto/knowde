"""系ネットワーク."""
from __future__ import annotations

from enum import Enum, auto
from functools import cached_property
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

from .errors import HeadingNotFoundError, SysNetNotFoundError, UnResolvedTermError
from .sysnode import Def, SysArg, SysNode


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
        if self == EdgeType.ANTI:
            g.add_edge(suc, pre, type=self)

    @cached_property
    def succ(self) -> Accessor:
        """エッジを辿って次を取得."""
        return succ_attr("type", self)

    @cached_property
    def pred(self) -> Accessor:
        """エッジを遡って前を取得."""
        return pred_attr("type", self)

    def get_succ(self, g: nx.DiGraph, n: Hashable) -> None | Hashable:
        """1つの先を返す."""
        return get_one(list(self.succ(g, n)))

    def get_pred(self, g: nx.DiGraph, n: Hashable) -> None | Hashable:
        """1つの前を返す."""
        return get_one(list(self.pred(g, n)))


def get_one(ls: list[Hashable]) -> None | Hashable:
    """1つまたはなしを取得."""
    if len(ls) == 0:
        return None
    return ls[0]


class SysNet(BaseModel):
    """系ネットワーク."""

    root: str
    g: NXGraph = Field(default_factory=DiGraph, init=False)
    _is_resolved: bool = PrivateAttr(default=False)

    def model_post_init(self, __context: Any) -> None:  # noqa: ANN401 D102
        self.g.add_node(self.root)

    def add(self, t: EdgeType, *path: SysArg) -> tuple[SysArg, ...]:
        """既存nodeから開始していない場合はrootからedgeを伸ばすように登録."""
        if len(path) > 0:
            first = path[0]
            _p = path if first in self.g else [self.root, *path]
            _p = [self._pre_add_edge(n) for n in _p]
            nx.add_path(self.g, _p, type=t)
        return path

    def _pre_add_edge(self, n: SysArg) -> str | Term:
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

    @property
    def headings(self) -> set[str]:
        """見出しセット."""
        ns = to_nodes(self.g, self.root, succ_attr("type", EdgeType.HEAD))
        return {str(n) for n in ns}

    def heading_path(self, n: SysNode) -> list[SysNode]:
        """直近の見出しパス."""
        paths = list(nx.shortest_simple_paths(self.g, self.root, n))
        if len(paths) == 0:
            raise HeadingNotFoundError
        p = paths[0]
        return [e for e in p if e in self.headings]

    def get(self, n: SysNode) -> SysArg:
        """文に紐づく用語があれば定義を返す."""
        if n not in self.g:
            raise SysNetNotFoundError

        match n:
            case str():
                term = EdgeType.DEF.get_pred(self.g, n)
                if term is None:
                    return n
                return Def(term=term, sentence=n)
            case Term():
                s = EdgeType.DEF.get_succ(self.g, n)
                if s is None:
                    return n
                return Def(term=n, sentence=s)
            case _:
                raise TypeError


def _add_resolve_edge(sn: SysNet, start: str, termd: dict) -> None:
    """(start)-[RESOLVE]->(marked sentence)."""
    for k, v in termd.items():
        s = next(EdgeType.DEF.succ(sn.g, k))  # 文
        EdgeType.RESOLVE.add_edge(sn.g, start, s)  # 文 -> 文
        if any(v):  # 空でない
            _add_resolve_edge(sn, str(s), v)
