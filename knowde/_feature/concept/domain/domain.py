"""concept domain."""
from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from typing import TypeVar
from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel, Field, field_serializer, field_validator
from uuid6 import uuid7

from knowde._feature._shared.timeutil import TZ
from knowde._feature.concept.error import NotExistsUidAccessError


class ConceptProp(BaseModel, frozen=True):
    """concept properties."""

    name: str
    explain: str | None = None


class Concept(ConceptProp, frozen=True):
    """domain model."""

    uid: UUID | None = None
    created: datetime | None = None
    updated: datetime | None = None

    @field_validator("created")
    def validate_created(cls, v: datetime) -> datetime:
        """Jst."""
        return v.astimezone(TZ)

    @field_validator("updated")
    def validate_updated(cls, v: datetime) -> datetime:
        """Jst."""
        return v.astimezone(TZ)

    @property
    def valid_uid(self) -> UUID:
        """Exists in db."""
        if self.uid is None:
            raise NotExistsUidAccessError
        return self.uid


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
