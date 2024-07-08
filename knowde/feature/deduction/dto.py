"""DTO for proposition."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel


class DeductionParam(BaseModel, frozen=True):
    """演繹パラメータ."""

    txt: str
    conclusion_id: UUID
    premise_ids: list[UUID]
    valid: bool = True


class DeductionAddCLIParam(BaseModel, frozen=True):
    """演繹CLIパラメータ."""

    txt: str
    conclusion_pref_uid: str
    valid: bool | None = True
    premise_pref_uids: list[str]
