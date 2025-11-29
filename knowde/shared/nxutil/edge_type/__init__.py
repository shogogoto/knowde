"""エッジの種類."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from enum import Enum, StrEnum, auto
from functools import cache, cached_property, reduce
from typing import TYPE_CHECKING

import networkx as nx

from knowde.shared.nxutil.errors import MultiEdgesError
from knowde.shared.nxutil.util import pred_attr, succ_attr

if TYPE_CHECKING:
    from knowde.shared.nxutil.types import Accessor


class Direction(Enum):
    """方向."""

    FORWARD = auto()
    BACKWARD = auto()
    BOTH = auto()


class EdgeType(StrEnum):
    """グラフ関係の種類."""

    # 文章構成
    SIBLING = auto()  # 兄弟 同階層 並列
    BELOW = auto()  # 配下 階層が下がる 直列

    # 意味的関係
    DEF = auto()  # term -> 文
    RESOLVED = auto()  # 用語解決関係 文 -> 文
    QUOTERM = auto()  # 引用用語 term -> def
    TO = auto()  # 依存
    EXAMPLE = auto()  # 具体

    # 付加的
    WHEN = auto()
    WHERE = auto()
    NUM = auto()
    BY = auto()
    REF = auto()

    # both
    ANTI = auto()  # 反対
    SIMILAR = auto()  # 類似

    @property
    def forward(self) -> tuple[EdgeType, Direction]:
        """正順."""
        return self, Direction.FORWARD

    @property
    def backward(self) -> tuple[EdgeType, Direction]:
        """逆順."""
        return self, Direction.BACKWARD

    @property
    def both(self) -> tuple[EdgeType, Direction]:
        """両順."""
        return self, Direction.BOTH

    def add_edge(self, g: nx.DiGraph, pre: Hashable, suc: Hashable) -> None:
        """エッジ追加."""
        g.add_edge(pre, suc, type=self)

    def add_path(
        self,
        g: nx.DiGraph,
        *ns: Hashable,
        cvt: Callable[[Hashable], Hashable] = lambda x: x,
    ) -> list[Hashable]:
        """連続追加."""
        ls = [cvt(n) for n in ns]
        nx.add_path(g, ls, type=self)
        return ls

    @cached_property
    def succ(self) -> Accessor:
        """エッジを辿って次を取得."""
        return succ_attr("type", self)

    @cached_property
    def pred(self) -> Accessor:
        """エッジを遡って前を取得."""
        return pred_attr("type", self)

    def get_succ_or_none(self, g: nx.DiGraph, n: Hashable) -> Hashable | None:
        """1つの先を返す."""
        return _get_one_or_none(list(self.succ(g, n)), self, n)

    def get_pred_or_none(self, g: nx.DiGraph, n: Hashable) -> Hashable | None:
        """1つの前を返す."""
        return _get_one_or_none(list(self.pred(g, n)), self, n)

    def subgraph(self, g: nx.DiGraph) -> nx.DiGraph:
        """同じタイプのエッジと繋がったノードを持つサブグラフ."""
        return _etype_subgraph(g, self)

    @cached_property
    def arrow(self) -> str:
        """cypherの矢印表現."""
        return f"{self.name}"


@cache
def etype_subgraph(g: nx.DiGraph, *ts: EdgeType) -> nx.DiGraph:
    """キャッシュありサブグラフ."""
    gs = [t.subgraph(g) for t in ts]
    return reduce(nx.compose, gs)


@cache
def _etype_subgraph(g: nx.DiGraph, t: EdgeType) -> nx.DiGraph:
    nodes = set()
    for u, v, data in g.edges(data=True):
        if data["type"] == t:
            nodes.add(u)
            nodes.add(v)
    return nx.subgraph(g, nodes)


def _get_one_or_none(ls: list[Hashable], t: EdgeType, src: Hashable) -> Hashable | None:
    """1つまたはなしを取得."""
    match len(ls):
        case 0:
            return None
        case 1:
            return ls[0]
        case _:
            msg = (
                f"'{src}'から複数の関係がヒットしました. 1つだけに修正してね: {t} \n\t"
                + "\n\t".join(map(str, ls))
            )
            raise MultiEdgesError(msg)


def is_root(g: nx.DiGraph, n: Hashable, et: EdgeType) -> bool:
    """graphのrootのみを取得."""
    has_to = len(list(et.succ(g, n))) > 0
    has_from = len(list(et.pred(g, n))) == 0
    return has_to and has_from


def is_leaf(g: nx.DiGraph, n: Hashable, et: EdgeType) -> bool:
    """graphの先端のみを取得."""
    has_refer = len(list(et.pred(g, n))) > 0
    has_referred = len(list(et.succ(g, n))) == 0
    return has_refer and has_referred
