from __future__ import annotations

from pydantic import Field

from knowde._feature._shared.domain import Entity


class Proposition(Entity, frozen=True):
    """命題."""

    text: str = Field(title="文章")
