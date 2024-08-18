"""Data Transfer Object."""
from __future__ import annotations

from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel

from knowde.complex.definition.domain.domain import DefinitionParam


class BookParam(BaseModel, frozen=True):
    """本作成パラメータ."""

    title: str
    author_name: str | None = None


class RefDefParam(BaseModel, frozen=True):
    """引用付き定義."""

    ref_uid: UUID
    name: str
    explain: str

    def to_defparam(self) -> DefinitionParam:
        """Convert."""
        return DefinitionParam(name=self.name, explain=self.explain)
