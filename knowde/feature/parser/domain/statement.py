"""言明."""
from __future__ import annotations

from typing import TYPE_CHECKING

from lark import Token, Tree, Visitor
from networkx import DiGraph
from pydantic import BaseModel, Field

from knowde.core.types import NXGraph
from knowde.feature.parser.domain.domain import Heading

if TYPE_CHECKING:
    from lark.tree import Branch


def scan_statements(t: Tree) -> list[str]:
    """言明の文字列を抜き出す."""
    types = ["ONELINE", "MULTILINE"]

    def _pred(b: Branch) -> bool:
        return isinstance(b, Token) and b.type in types

    return [str(s) for s in t.scan_values(_pred)]


line_types = ["ONELINE", "MULTILINE"]


class LineMismatchError(Exception):
    """lineの値が見つからないはずがない."""


def get_line(t: Tree) -> str:
    """Line treeから値を1つ返す."""
    ls = [c for c in t.children if isinstance(c, Token) and c.type in line_types]
    if len(ls) == 1:
        return ls[0]
    raise LineMismatchError


class NameMismatchError(Exception):
    """nameの値が見つからないはずがない."""


class StatementVisitor(BaseModel, Visitor):
    """言明の処理."""

    current_heading: Heading | None = None
    g: NXGraph = Field(default_factory=DiGraph)
    # def name(self, t: Tree) -> None:
    #     print(t)

    def line(self, t: Tree) -> None:  # noqa: D102
        pass
        # print("S" * 80)
        # print(t)
        # print(get_alias(t))
        # print(get_line(t))

    def define(self, t: Tree) -> None:  # noqa: D102
        pass
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
