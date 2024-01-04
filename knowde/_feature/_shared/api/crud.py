from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, TypeVar
from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel
from starlette.status import HTTP_204_NO_CONTENT

from knowde._feature._shared.domain import DomainModel
from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.util import LabelUtil  # noqa: TCH001

if TYPE_CHECKING:
    from fastapi import APIRouter

L = TypeVar("L", bound=LBase)
M = TypeVar("M", bound=DomainModel)


class CRUDRouter(BaseModel, Generic[L, M], frozen=True):
    util: LabelUtil
    ls_all: Callable[[], list[M]] | None = None

    def create(
        self,
        router: APIRouter,
    ) -> APIRouter:
        """labelに対応したCRUD APIの基本的な定義."""

        @router.get("")
        def _get() -> list[M]:
            if self.ls_all is None:
                return self.util.find_all().to_model()
            return self.ls_all()

        @router.get("/completion")
        def _complete(pref_uid: str) -> M:
            return self.util.complete(pref_uid).to_model()

        @router.delete(
            "/{uid}",
            status_code=HTTP_204_NO_CONTENT,
            response_model=None,
        )
        def _delete(uid: UUID) -> None:
            self.util.delete(uid)

        return router
