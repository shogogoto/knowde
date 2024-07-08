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


class ReplacePremisesParam(BaseModel, frozen=True):
    """前提を置換するCLIパラメータ."""

    deduction_pref_uid: str
    premise_pref_uids: list[str]


class ReplaceConclusionParam(BaseModel, frozen=True):
    """結論を置換するCLIパラメータ."""

    deduction_pref_uid: str
    conclusion_pref_uid: str
