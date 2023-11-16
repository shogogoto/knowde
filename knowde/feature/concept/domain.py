"""concept domain."""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel

if TYPE_CHECKING:
    from datetime import datetime


class Concept(BaseModel, frozen=True):
    """domain model."""

    uid: UUID | None = None
    name: str
    explain: str | None = None
    created: datetime | None = None
    updated: datetime | None = None

    def exists(self) -> bool:
        """Exists in db."""
        return self.uid is not None
