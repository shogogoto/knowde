"""マージされて同じTermを持つDef同士を、マージ."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Hashable, TypeAlias

from lark import Token
from pydantic import BaseModel, Field

from knowde.complex.__core__.sysnet.errors import QuotermNotFoundError
from knowde.complex.__core__.sysnet.sysnode import (
    Def,
    DummySentence,
    Duplicable,
    SysArg,
)
from knowde.primitive.__core__.nxutil import replace_node
from knowde.primitive.__core__.nxutil.edge_type import Direction, EdgeType
from knowde.primitive.term import Term
from knowde.primitive.term.markresolver import MarkResolver

if TYPE_CHECKING:
    import networkx as nx


Converter: TypeAlias = Callable[[SysArg], Any]


class DirectedEdge(BaseModel, frozen=True, arbitrary_types_allowed=True):
    """treeで定義された関係."""

    t: EdgeType
    d: Direction
    nodes: list[SysArg | Token]  # Tokenを指定しないとstrに型変換される

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
            v.add_edge(g, node2sentence)


def node2sentence(n: SysArg) -> str | DummySentence | Token:
    """関係のハブとなる文へ."""
    match n:
        case Term():
            d = Def.dummy(n)
            return d.sentence
        case str() | Duplicable():
            return n
        case Def():
            return n.sentence
        case _:
            msg = f"{type(n)}: {n} is not allowed."
            raise TypeError(msg)


def is_quoterm(v: SysArg) -> bool:
    """filter用."""
    return isinstance(v, Token) and v.type == "QUOTERM"


# def get_ifdef(g: nx.DiGraph, n: SysNode) -> None:
#     pass


def replace_quoterms(g: nx.DiGraph, resolver: MarkResolver) -> None:
    """引用用語を1文に置換."""
    for qt in [n for n in g.nodes if is_quoterm(n)]:
        name = qt.replace("`", "")
        if name not in resolver.lookup:
            msg = f"'{name}'は用語として定義されていません"
            raise QuotermNotFoundError(msg)
        term = resolver.lookup[name]
        s = EdgeType.DEF.get_succ_or_none(g, term)
        if s is None:
            raise TypeError
        replace_node(g, qt, s)
