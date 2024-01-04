from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Generic, TypeVar

from pydantic import BaseModel

from knowde._feature._shared.api.basic_param import (
    CompleteParam,
    DeleteParam,
    ListParam,
)
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

    def set_router(
        self,
        router: APIRouter,
    ) -> APIRouter:
        """labelに対応したCRUD APIの基本的な定義."""
        ListParam.api(router, lambda: self.util.find_all().to_model(), "get")
        DeleteParam.api(router, self.util.delete, "delete")
        CompleteParam.api(
            router,
            lambda pref_uid: self.util.complete(pref_uid=pref_uid).to_model(),
            "complete",
        )

        return router
