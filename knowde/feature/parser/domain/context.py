"""about context."""
from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, Hashable

from lark import Token, Transformer, Tree

from knowde.feature.parser.domain.domain import get_line
from knowde.feature.parser.domain.errors import ContextMismatchError

if TYPE_CHECKING:
    from networkx import DiGraph


class ContextType(Enum):
    """文脈の種類."""

    THUS = auto()
    CAUSE = auto()
    ANTONYM = auto()
    EXAMPLE = auto()
    GENERAL = auto()
    REF = auto()
    NUM = auto()


class EdgeType(Enum):
    """グラフ関係の種類."""

    TO = auto()
    ANTI = auto()
    ABSTRACT = auto()
    REF = auto()
    LIST = auto()


def ctxtree2tuple(t: Tree) -> tuple[ContextType, str]:
    """Ctx tree to tuple."""
    ctx_type: ContextType = t.children[0]
    v = t.children[1]
    return ctx_type, get_line(v)


def add_context(g: DiGraph, x1: Hashable, x2: Hashable, t: ContextType) -> None:
    """グラフに文脈関係を追加.

    x1 -> x2
    """
    match t:
        case ContextType.THUS:
            g.add_edge(x1, x2, ctx=EdgeType.TO)
        case ContextType.CAUSE:
            g.add_edge(x2, x1, ctx=EdgeType.TO)
        case ContextType.ANTONYM:
            g.add_edge(x1, x2, ctx=EdgeType.ANTI)
            g.add_edge(x2, x1, ctx=EdgeType.ANTI)
        case ContextType.EXAMPLE:
            g.add_edge(x2, x1, ctx=EdgeType.ABSTRACT)
        case ContextType.GENERAL:
            g.add_edge(x1, x2, ctx=EdgeType.ABSTRACT)
        case ContextType.REF:
            g.add_edge(x1, x2, ctx=EdgeType.REF)
        case ContextType.NUM:
            nums = [
                (u, v, d)
                for u, v, d in g.edges(data=True)
                if d.get("ctx") == EdgeType.LIST
            ]
            i = len(nums)
            g.add_edge(x1, x2, ctx=EdgeType.LIST, i=i)
        case _:
            raise ContextMismatchError


class TContext(Transformer):
    """context transformer."""

    def THUS(self, _tok: Token) -> ContextType:  # noqa: D102 N802
        return ContextType.THUS

    def CAUSE(self, _tok: Token) -> ContextType:  # noqa: D102 N802
        return ContextType.CAUSE

    def ANTONYM(self, _tok: Token) -> ContextType:  # noqa: D102 N802
        return ContextType.ANTONYM

    def EXAMPLE(self, _tok: Token) -> ContextType:  # noqa: D102 N802
        return ContextType.EXAMPLE

    def GENERAL(self, _tok: Token) -> ContextType:  # noqa: D102 N802
        return ContextType.GENERAL

    def REF(self, _tok: Token) -> ContextType:  # noqa: D102 N802
        return ContextType.REF

    def NUM(self, _tok: Token) -> ContextType:  # noqa: D102 N802
        return ContextType.NUM
