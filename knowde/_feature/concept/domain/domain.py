"""concept domain."""
from __future__ import annotations

from typing import TypeVar
from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel, Field, field_serializer
from uuid6 import uuid7

from knowde._feature._shared import DomainModel


class ConceptProp(BaseModel, frozen=True):
    """concept properties."""

    name: str
    explain: str | None = None


class Concept(ConceptProp, DomainModel, frozen=True):
    pass


T = TypeVar("T")


class AdjacentIdsProp(BaseModel, frozen=True):
    src_ids: list[str] = Field(
        default_factory=list,
        description="前方一致で検索",
    )
    dest_ids: list[str] = Field(
        default_factory=list,
        description="前方一致で検索",
    )


class SaveProp(AdjacentIdsProp, ConceptProp, frozen=True):
    uid: UUID = Field(default_factory=uuid7)

    @field_serializer("uid")
    def to_label(self, v: UUID) -> str:
        """UniqueIdPropertyはuuid4以外使えない."""
        return v.hex


class ChangeProp(BaseModel, frozen=True):
    """for change props."""

    name: str | None = None
    explain: str | None = None
