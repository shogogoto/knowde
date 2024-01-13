from uuid import UUID

from pydantic import BaseModel

from knowde._feature._shared.api.basic_param import AddParam


class NameParam(AddParam, frozen=True):
    name: str


class RefIdParam(BaseModel, frozen=True):
    ref_id: UUID


class SubReferenceParam(NameParam, RefIdParam, frozen=True):
    pass
