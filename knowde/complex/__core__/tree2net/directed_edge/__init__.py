"""マージされて同じTermを持つDef同士を、マージ."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Hashable, TypeAlias

from pydantic import BaseModel, Field

from knowde.primitive.__core__.nxutil.edge_type import Direction, EdgeType

if TYPE_CHECKING:
    import networkx as nx


Converter: TypeAlias = Callable[[Hashable], Any]


class DirectedEdge(BaseModel, frozen=True):
    """中間生成物."""

    t: EdgeType
    d: Direction
    nodes: list[Hashable]

    def add(self, g: nx.DiGraph, cvt: Converter) -> None:
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
    """中間生成物."""

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
