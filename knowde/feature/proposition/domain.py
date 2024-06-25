"""domain."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from knowde._feature._shared.domain import Entity

if TYPE_CHECKING:
    from knowde.feature.definition.domain.domain import Definition


class Proposition(Entity, frozen=True):
    """命題."""

    value: str = Field(title="文章")


class Theorem(Proposition, frozen=True):
    """定理(名前付き命題)."""

    name: str


class Argument(BaseModel, frozen=True):
    """論証."""

    value: str = Field(title="文章")
    premises: list[Proposition | Theorem | Definition] = Field(
        default_factory=list,
        title="前提",
    )
    conclusion: Proposition = Field(title="結論")
    valid: bool = Field(description="結論の正しさ")
