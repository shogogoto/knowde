from __future__ import annotations

from enum import Enum  # noqa: TCH003
from typing import Generic, TypeVar
from uuid import UUID  # noqa: TCH003

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from knowde._feature._shared.domain import DomainModel
from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.util import LabelUtil  # noqa: TCH001

L = TypeVar("L", bound=LBase)
M = TypeVar("M", bound=DomainModel)


class CRUDRouter(BaseModel, Generic[L, M], frozen=True):
    util: LabelUtil

    def create(
        self,
        prefix: str,
        tags: list[str | Enum],
    ) -> APIRouter:
        """labelに対応したCRUD APIの基本的な定義."""
        r = APIRouter(prefix=prefix, tags=tags)

        @r.get("")
        def _get() -> list[M]:
            return self.util.find_all().to_model()

        @r.get(
            "/completion",
            status_code=HTTP_201_CREATED,
        )
        def _complete(pref_uid: str) -> M:
            return self.util.complete(pref_uid).to_model()

        @r.delete(
            "/{uid}",
            status_code=HTTP_204_NO_CONTENT,
            response_model=None,
        )
        def _delete(uid: UUID) -> None:
            self.util.delete(uid)

        return r
