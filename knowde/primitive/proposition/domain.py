"""domain."""
from __future__ import annotations

from pydantic import Field

from knowde.core.domain import Entity


class Proposition(Entity, frozen=True):
    """命題."""

    text: str = Field(title="文章")

    @property
    def output(self) -> str:
        """For cli output."""
        return f"{self.text} ({self.valid_uid})"
