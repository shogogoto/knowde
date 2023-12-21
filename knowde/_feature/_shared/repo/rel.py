from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel

from knowde._feature._shared.domain import DomainModel
from knowde._feature._shared.repo.label import LBase

L = TypeVar("L", bound=LBase)
M = TypeVar("M", bound=DomainModel)


class RelUtil(BaseModel, Generic[L, M], frozen=True):
    uid: UUID
