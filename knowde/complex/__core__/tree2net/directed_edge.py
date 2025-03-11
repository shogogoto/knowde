"""マージされて同じTermを持つDef同士を、マージ."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Hashable, TypeAlias

from lark import Token  # noqa: TCH002
from pydantic import BaseModel, Field

from knowde.complex.__core__.sysnet.sysfn import (
    arg2sentence,
)
from knowde.complex.__core__.sysnet.sysnode import KNArg
from knowde.primitive.__core__.nxutil.edge_type import Direction, EdgeType

if TYPE_CHECKING:
    import networkx as nx


Converter: TypeAlias = Callable[[KNArg], Any]


class DirectedEdge(BaseModel, frozen=True, arbitrary_types_allowed=True):
    """treeで定義された関係."""

    t: EdgeType
    d: Direction
    nodes: list[KNArg | Token]  # Tokenを指定しないとstrに型変換される

    def add_edge(self, g: nx.DiGraph, cvt: Converter) -> None:
        """方向付き追加."""
        ns = list(map(cvt, self.nodes))
        match self.d:
            case Direction.FORWARD:
                self.t.add_path(g, *ns)
            case Direction.BACKWARD:
                self.t.add_path(g, *reversed(ns))
            case Direction.BOTH:
                self.t.add_path(g, *ns)
                self.t.add_path(g, *reversed(ns))
            case _:
                raise TypeError


class DirectedEdgeCollection(BaseModel):
    """treeで定義された関係の集合."""

    values: list[DirectedEdge] = Field(default_factory=list)

    def append(self, t: EdgeType, d: Direction, *nodes: Hashable) -> None:  # noqa: D102
        v = DirectedEdge(t=t, d=d, nodes=list(nodes))
        self.values.append(v)

    def convert(self, cvt: Converter) -> list:
        """要素変換."""
        ls = []
        for v in self.values:
            ls.extend([cvt(n) for n in v.nodes])
        return [e for e in ls if e]

    def add_edges(self, g: nx.DiGraph) -> None:
        """graphへ関係を追加."""
        for v in self.values:
            v.add_edge(g, arg2sentence)
