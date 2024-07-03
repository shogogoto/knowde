"""domain."""
from __future__ import annotations

from pydantic import Field

from knowde._feature._shared.domain import Entity


class Proposition(Entity, frozen=True):
    """命題."""

    text: str = Field(title="文章")


class Deduction(Entity, frozen=True):
    """論証."""

    text: str = Field(title="文章")
    premises: list[Proposition] = Field(
        default_factory=list,
        title="前提",
    )
    conclusion: Proposition = Field(title="結論")
    valid: bool = Field(description="結論の正しさ")
