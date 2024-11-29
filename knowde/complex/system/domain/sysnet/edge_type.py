"""エッジタイプ."""
from __future__ import annotations

from enum import StrEnum, unique
from functools import cached_property
from typing import TYPE_CHECKING, Hashable

from knowde.complex.system.domain.nxutil import pred_attr, succ_attr
from knowde.complex.system.domain.nxutil.types import Accessor

if TYPE_CHECKING:
    import networkx as nx


@unique
class EdgeType(StrEnum):
    """グラフ関係の種類."""

    HEAD = "head"  # 見出しを配下にする
    SIBLING = "sibling"  # 兄弟 同階層 並列
    BELOW = "below"  # 配下 階層が下がる 直列
    DEF = "def"  # term -> 文
    RESOLVED = "resolved"  # 用語解決関係 文 -> 文

    TO = "to"  # 依存
    CONCRETE = "concrete"  # 具体
    WHEN = "when"

    # bidicrectional
    ANTI = "anti"  # 反対

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
