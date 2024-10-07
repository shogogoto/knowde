"""parser utils."""
from __future__ import annotations

from lark import Token, Tree, Visitor
from pydantic import BaseModel, Field

from knowde.core.types import NXGraph
from knowde.feature.parser.domain.parser.transfomer.heading import Heading

from .const import LINE_TYPES
from .errors import LineMismatchError


def get_line(t: Tree) -> str:
    """Line treeから値を1つ返す."""
    # 直下がlineだった場合
    cl = t.children
    first = cl[0]
    if isinstance(first, Token) and first.type in LINE_TYPES:
        return str(first)
    if isinstance(first, Tree):
        if first.data == "ctx":
            return get_line(first.children[1])
        return get_line(first)
    raise LineMismatchError


class HeadingVisitor(BaseModel, Visitor):
    """どの見出しでのvisitか把握."""

    current: Heading | None = None
    G: NXGraph = Field(default_factory=NXGraph)

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
        prev = self.current
        self.current = t.children[0]
        if prev is None:
            self.G.add_node(self.current)
        else:
            self.G.add_edge(prev, self.current)
