"""DTO for proposition."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel


class DeductionParam(BaseModel, frozen=True):
    """演繹パラメータ."""

    txt: str
    premise_ids: list[UUID]
    conclusion_id: UUID
    valid: bool = True
