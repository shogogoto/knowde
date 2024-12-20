"""networkx関連."""
from __future__ import annotations

from enum import Enum, auto
from functools import cached_property
from pprint import pp
from typing import Any, Callable, Hashable, Iterator

import networkx as nx

from .types import Accessor, Edges


def nxprint(g: nx.DiGraph, detail: bool = False) -> None:  # noqa: FBT001 FBT002
    """確認用."""
    print("")  # noqa: T201
    nx.write_network_text(g)
    if detail:
        pp(nx.to_dict_of_dicts(g))


def to_nested(
    g: nx.DiGraph,
    start: Hashable,
    f: Accessor,
) -> dict:
    """有向グラフから入れ子の辞書を作成."""

    def _f(n: Hashable) -> dict:
        nlist = list(f(g, n))
        if not nlist:
            return {}
        return {anode: _f(anode) for anode in nlist}

    return _f(start)


def to_nodes(
    g: nx.DiGraph,
    start: Hashable,
    f: Accessor,
) -> set[Hashable]:
    """有向グラフを辿ってノードを取得."""
    s = set()

    def _f(n: Hashable) -> None:
        nlist = list(f(g, n))
        s.add(n)
        s.union([_f(anode) for anode in nlist])

    _f(start)
    return s


def succ_attr(attr_name: str, value: Any) -> Accessor:  # noqa: ANN401
    """次を関係の属性から辿る."""

    def _f(g: nx.DiGraph, start: Hashable) -> Iterator[Hashable]:
        for succ in g.successors(start):
            if g.edges[start, succ].get(attr_name) == value:
                _f(g, succ)
                yield succ

    return _f


def pred_attr(attr_name: str, value: Any) -> Accessor:  # noqa: ANN401
    """前を関係の属性から辿る."""

    def _f(g: nx.DiGraph, start: Hashable) -> Iterator[Hashable]:
        for pred in g.predecessors(start):
            if g.edges[pred, start].get(attr_name) == value:
                _f(g, pred)
                yield pred

    return _f


def filter_edge_attr(g: nx.DiGraph, name: str, value: Any) -> nx.DiGraph:  # noqa: ANN401
    """ある属性のエッジのみを抽出する関数を返す."""

    def _f(u: Hashable, v: Hashable) -> bool:
        return g[u][v][name] == value

    return nx.subgraph_view(g, filter_edge=_f)


def _to_paths(g: nx.DiGraph, pairs: Edges) -> list[list[Hashable]]:
    paths = []
    for u, v in pairs:
        try:
            p = list(nx.shortest_path(g, u, v))
            paths.append(p)
        except nx.NetworkXNoPath:  # noqa: PERF203
            continue
    return paths


def leaf_paths(g: nx.DiGraph, tgt: Hashable, t: Any) -> list[list[Hashable]]:  # noqa: ANN401
    """入力ノードから特定の関係を遡って依存先がないノードまでのパスを返す."""
    sub = filter_edge_attr(g, "type", t)
    edges = [
        (tgt, n) for n in sub.nodes if sub.out_degree(n) == 0 and sub.degree(n) != 0
    ]
    return _to_paths(sub, edges)


def axiom_paths(g: nx.DiGraph, tgt: Hashable, t: Any) -> list[list[Hashable]]:  # noqa: ANN401
    """入力ノードから特定の関係を遡って依存元がないノードまでのパスを返す."""
    sub = filter_edge_attr(g, "type", t)
    pairs = [
        (n, tgt) for n in sub.nodes if sub.in_degree(n) == 0 and sub.degree(n) != 0
    ]
    return _to_paths(sub, pairs)


def nxconvert(g: nx.DiGraph, convert: Callable[[Hashable], Hashable]) -> nx.DiGraph:
    """ネットワークのノード型を変換."""
    new = nx.DiGraph()
    new.add_nodes_from([convert(n) for n in g.nodes])
    new.add_edges_from([(convert(u), convert(v), d) for u, v, d in g.edges(data=True)])
    return new


class Direction(Enum):
    """方向."""

    FORWARD = auto()
    BACKWARD = auto()
    BOTH = auto()


class EdgeType(Enum):
    """グラフ関係の種類."""

    HEAD = auto()  # 見出しを配下にする
    SIBLING = auto()  # 兄弟 同階層 並列
    BELOW = auto()  # 配下 階層が下がる 直列
    DEF = auto()  # term -> 文
    RESOLVED = auto()  # 用語解決関係 文 -> 文

    TO = auto()  # 依存
    EXAMPLE = auto()  # 具体
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

    def get_succ(self, g: nx.DiGraph, n: Hashable) -> None | Hashable:
        """1つの先を返す."""
        return _get_one(list(self.succ(g, n)))

    def get_pred(self, g: nx.DiGraph, n: Hashable) -> None | Hashable:
        """1つの前を返す."""
        return _get_one(list(self.pred(g, n)))


def _get_one(ls: list[Hashable]) -> None | Hashable:
    """1つまたはなしを取得."""
    if len(ls) == 0:
        return None
    return ls[0]


def replace_node(g: nx.DiGraph, old: Hashable, new: Hashable) -> None:
    """エッジを保ってノードを置換."""
    g.add_node(new)
    for pred in g.predecessors(old):
        g.add_edge(pred, new, **g.get_edge_data(pred, old))

    for succ in g.successors(old):
        g.add_edge(new, succ, **g.get_edge_data(old, succ))
    g.remove_node(old)
