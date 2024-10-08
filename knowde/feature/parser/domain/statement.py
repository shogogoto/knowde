"""言明."""
from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, Hashable, Self

from lark import Token, Tree
from networkx import DiGraph
from pydantic import BaseModel, Field

from knowde.core.types import NXGraph
from knowde.feature.parser.domain.errors import ContextMismatchError
from knowde.feature.parser.domain.parser.const import LINE_TYPES
from knowde.feature.parser.domain.parser.transfomer.context import ContextType
from knowde.feature.parser.domain.parser.utils import HeadingVisitor, get_line

if TYPE_CHECKING:
    from lark.tree import Branch


def scan_statements(t: Tree) -> list[str]:
    """言明の文字列を抜き出す."""

    def _pred(b: Branch) -> bool:
        return isinstance(b, Token) and b.type in LINE_TYPES

    return [str(s) for s in t.scan_values(_pred)]


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


class StatementVisitor(HeadingVisitor):
    """言明の処理."""

    g: NXGraph = Field(default_factory=DiGraph, description="言明ネットワーク")

    def block(self, t: Tree) -> None:
        """主文とその文脈を解決する."""
        line = get_line(t)
        for c in t.children[1:]:
            if isinstance(c, Tree) and c.data == "ctx":
                ctx_type, v = ctxtree2tuple(c)
                # ctx_type: ContextType = c.children[0]
                # v = get_line(c.children[1])
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
        # print("S" * 80)
        # print(t)
        # print(get_alias(t))
        # print(get_line(t))

    def define(self, t: Tree) -> None:
        """名前と言明の辞書を作る."""
        # print("D" * 80)
        # print(t)
        # print(get_alias(t))
        # print(get_names(t))
        # print(get_line(t))


class Statement(BaseModel, frozen=True):
    """言明."""

    value: str
    g: NXGraph

    @classmethod
    def create(cls, value: str, t: Tree) -> Self:  # noqa: D102
        v = StatementVisitor()
        v.visit(t)
        if value not in v.g:
            msg = "Not Found!"
            raise KeyError(msg)
        return cls(value=value, g=v.g)

    @property
    def thus(self) -> list[str]:  # noqa: D102
        return self._ctx_to(EdgeType.TO)

    @property
    def cause(self) -> list[str]:  # noqa: D102
        return self._ctx_from(EdgeType.TO)

    @property
    def example(self) -> list[str]:  # noqa: D102
        return self._ctx_from(EdgeType.ABSTRACT)

    @property
    def general(self) -> list[str]:  # noqa: D102
        return self._ctx_to(EdgeType.ABSTRACT)

    @property
    def ref(self) -> list[str]:  # noqa: D102
        return self._ctx_to(EdgeType.REF)

    @property
    def list(self) -> list[str]:  # noqa: D102
        # ls = [
        #     (v, d["i"])
        #     for _u, v, d in self.g.edges(self.value, data=True)
        #     if d.get("ctx") == EdgeType.LIST
        # ]
        return self._ctx_to(EdgeType.LIST)

    def _ctx_to(self, t: EdgeType) -> list[str]:
        return [
            v for _u, v, d in self.g.edges(self.value, data=True) if d.get("ctx") == t
        ]

    def _ctx_from(self, t: EdgeType) -> list[str]:
        return [
            u
            for u, v, d in self.g.edges(data=True)
            if d.get("ctx") == t and v == self.value
        ]
