"""言明."""
from __future__ import annotations

from typing import TYPE_CHECKING, Self

from pydantic import BaseModel

from knowde.core.types import NXGraph
from knowde.feature.parser.domain.parser.utils import HeadingVisitor
from knowde.feature.parser.domain.statement.visitor import EdgeType, StatementVisitor

if TYPE_CHECKING:
    from lark import Tree


class LineVisitor(HeadingVisitor):
    """言明の文字列を抜き出す."""

    # def line(self, t: Tree) -> None:
    #     print(t)


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
