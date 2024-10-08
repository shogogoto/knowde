"""言明."""
from __future__ import annotations

from enum import Enum, auto

from pydantic import BaseModel


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


class StatementGraph(BaseModel):
    """言明ネットワーク."""
