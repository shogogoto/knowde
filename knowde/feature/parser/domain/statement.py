"""言明."""
from __future__ import annotations

from typing import TYPE_CHECKING

from lark import Token, Tree, Visitor
from pydantic import BaseModel

from knowde.feature.parser.domain.domain import Heading

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

    def _set_heading(self, t: Tree) -> None:
        pass

    # def block(self, t: Tree) -> None:
    #     print("S" * 80)
    #     print(t)

    # def h1(self, t: Tree) -> None:
    #     print("1" * 80)
