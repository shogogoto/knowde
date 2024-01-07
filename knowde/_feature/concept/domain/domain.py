"""concept domain."""
from __future__ import annotations

from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_serializer

from knowde._feature._shared import DomainModel
from knowde._feature._shared.api.basic_param import AddParam, ChangeParam
from knowde._feature._shared.api.param import ApiParam


class ConceptProp(AddParam, frozen=True):
    """concept properties."""

    name: str
    explain: str | None = Field(None, description="説明文")


class Concept(ConceptProp, DomainModel, frozen=True):
    pass


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
    uid: UUID = Field(default_factory=uuid4)

    @field_serializer("uid")
    def to_label(self, v: UUID) -> str:
        """UniqueIdPropertyはuuid4以外使えない."""
        return v.hex


class ChangeProp(ApiParam, frozen=True):
    """for change props."""

    name: str | None = Field(None, description="名前")
    explain: str | None = Field(None, description="説明文")


class ConceptChangeParam(ChangeParam, frozen=True):
    name: str | None = Field(None, description="名前")
    explain: str | None = Field(None, description="説明文")
