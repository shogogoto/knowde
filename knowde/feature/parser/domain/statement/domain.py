"""言明."""
from __future__ import annotations

from enum import Enum, auto

from pydantic import BaseModel

from knowde.core.types import NXGraph


class EdgeType(Enum):
    """グラフ関係の種類."""

    TO = auto()
    ANTI = auto()
    ABSTRACT = auto()
    REF = auto()
    LIST = auto()


class Statement(BaseModel, frozen=True):
    """言明."""

    value: str

    def pick(self) -> list[str]:
        """埋め込まれた名を取得."""


class ContextedStatement(BaseModel, frozen=True):
    """文脈中での言明."""

    start: str
    g: NXGraph

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
            v for _u, v, d in self.g.edges(self.start, data=True) if d.get("ctx") == t
        ]

    def _ctx_from(self, t: EdgeType) -> list[str]:
        return [
            u
            for u, v, d in self.g.edges(data=True)
            if d.get("ctx") == t and v == self.start
        ]


class StatementGraph(BaseModel):
    """言明ネットワーク."""

    g: NXGraph

    @property
    def strings(self) -> list[str]:
        """言明文字列一覧."""
        return [str(n) for n in self.g.nodes]

    def contexted(self, v: str) -> ContextedStatement:
        """文脈付き言明を返す."""
        return ContextedStatement(start=v, g=self.g)
