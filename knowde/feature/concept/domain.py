"""concept domain."""
from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel


class Concept(BaseModel, frozen=True):
    """domain model."""

    uid: UUID | None = None
    name: str
    explain: str | None = None
    created: datetime | None = None
    updated: datetime | None = None
