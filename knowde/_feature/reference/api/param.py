from uuid import UUID

from pydantic import BaseModel


class NameParam(BaseModel, frozen=True):
    name: str


class RefIdParam(BaseModel, frozen=True):
    ref_id: UUID


class SubReferenceParam(NameParam, RefIdParam, frozen=True):
    pass
