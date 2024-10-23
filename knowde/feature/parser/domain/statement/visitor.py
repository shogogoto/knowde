"""言明Visitor."""
from __future__ import annotations

from typing import TYPE_CHECKING, Hashable

from lark import Tree
from pydantic import Field

from knowde.core.types import NXGraph
from knowde.feature.parser.domain.parser.transfomer.context import ContextType
from knowde.feature.parser.domain.parser.utils import HeadingVisitor, get_line
from knowde.feature.parser.domain.statement.domain import EdgeType, StatementGraph

if TYPE_CHECKING:
    from networkx import DiGraph


def ctxtree2tuple(t: Tree) -> tuple[ContextType, str]:
    """Ctx tree to tuple."""
    ctx_type: ContextType = t.children[0]
    v = t.children[1]
    return ctx_type, get_line(v)


class ContextMismatchError(Exception):
    """未定義の文脈DA!."""


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
            raise ContextMismatchError(x1, x2, t)


class StatementVisitor(HeadingVisitor):
    """言明の処理."""

    g: NXGraph = Field(default_factory=NXGraph, description="言明ネットワーク")

    def block(self, t: Tree) -> None:
        """主文とその文脈を解決する."""
        line = get_line(t)
        for c in t.children[1:]:
            if isinstance(c, Tree) and c.data == "ctx":
                ctx_type, v = ctxtree2tuple(c)
                add_context(self.g, line, v, ctx_type)
            if isinstance(c, Tree) and c.data == "block":
                blc_first = c.children[0]
                if isinstance(blc_first, Tree) and blc_first.data == "ctx":
                    ctx_type, v = ctxtree2tuple(blc_first)
                    add_context(self.g, line, v, ctx_type)

    def line(self, t: Tree) -> None:
        """Aliasと言明の辞書を作る.

        Aliasは意味を持たない記号である点が用語とは異なる
        """
        s = t.children[0]
        self.g.add_node(s)

    def define(self, t: Tree) -> None:
        """名前と言明の辞書を作る."""
        # print("D" * 80)
        # print(t)
        # print(get_alias(t))
        # print(get_names(t))
        # print(get_line(t))


def tree2statements(t: Tree) -> StatementGraph:
    """解析木から言明ネットワークへ変換."""
    """"""
    v = StatementVisitor()
    v.visit_topdown(t)
    return StatementGraph(g=v.g)
