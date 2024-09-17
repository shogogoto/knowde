"""言明."""
from __future__ import annotations

from typing import TYPE_CHECKING, Self

from lark import Token, Tree, Visitor
from networkx import DiGraph
from pydantic import BaseModel, Field

from knowde.core.types import NXGraph
from knowde.feature.parser.domain.context import (
    EdgeType,
    add_context,
    ctxtree2tuple,
)
from knowde.feature.parser.domain.domain import Heading, get_line

if TYPE_CHECKING:
    from lark.tree import Branch


def scan_statements(t: Tree) -> list[str]:
    """言明の文字列を抜き出す."""
    types = ["ONELINE", "MULTILINE"]

    def _pred(b: Branch) -> bool:
        return isinstance(b, Token) and b.type in types

    return [str(s) for s in t.scan_values(_pred)]


class StatementVisitor(BaseModel, Visitor):
    """言明の処理."""

    current_heading: Heading | None = None
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

    def h1(self, t: Tree) -> None:  # noqa: D102
        self._set_heading(t)

    def h2(self, t: Tree) -> None:  # noqa: D102
        self._set_heading(t)

    def h3(self, t: Tree) -> None:  # noqa: D102
        self._set_heading(t)

    def h4(self, t: Tree) -> None:  # noqa: D102
        self._set_heading(t)

    def h5(self, t: Tree) -> None:  # noqa: D102
        self._set_heading(t)

    def h6(self, t: Tree) -> None:  # noqa: D102
        self._set_heading(t)

    def _set_heading(self, t: Tree) -> None:
        self.current_heading = t.children[0]


class Statement(BaseModel, frozen=True):
    """言明."""

    value: str
    g: NXGraph

    @classmethod
    def create(cls, value: str, g: NXGraph) -> Self:  # noqa: D102
        if value not in g:
            msg = "Not Found!"
            raise KeyError(msg)
        return cls(value=value, g=g)

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
