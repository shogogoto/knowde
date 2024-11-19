"""系ネットワーク."""
from __future__ import annotations

from enum import Enum, auto
from typing import Hashable

import networkx as nx
from networkx import DiGraph
from pydantic import BaseModel, Field

from knowde.complex.system.domain.sysnode import Def, SysNodeType
from knowde.core.types import NXGraph

from .term.domain import Term


class EdgeType(Enum):
    """グラフ関係の種類."""

    HEAD = auto()  # 見出しを配下にする
    BELOW = auto()  # 配下 階層が下がる 直列
    SIBLING = auto()  # 兄弟 同階層 並列
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


class SystemNetwork(BaseModel):
    """系ネットワーク."""

    root: str
    g: NXGraph = Field(default_factory=DiGraph, init=False)

    # 見出しだけstr限定だからtype hint用にメソッドを用意した
    def head(self, pre: str, succ: str) -> None:
        """見出し追加."""
        EdgeType.HEAD.add_edge(self.g, pre, succ)

    def add(self, t: EdgeType, pre: SysNodeType, suc: SysNodeType) -> None:
        """エッジ追加."""
        # nodeはtermかsentenceの2種類しかない
        #   定義はedgeによって表現される
        pre_ = self._add(pre)
        suc_ = self._add(suc)
        t.add_edge(self.g, pre_, suc_)

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

    def resolve(self) -> None:
        """名前解決."""
        # mt = MergedTerms(terms=[n for n in self.g.nodes if isinstance(n, Term)])
        # tn = mt.to_resolver()
        # tn.

    # def head_path(self, n: Hashable) -> None:
    #     """直近の見出しパス."""
