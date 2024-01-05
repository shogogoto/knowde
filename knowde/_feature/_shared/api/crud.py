from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature._shared.repo.util import LabelUtil  # noqa: TCH001

from .basic_param import (
    CompleteParam,
    ListParam,
    RemoveParam,
)

if TYPE_CHECKING:
    from fastapi import APIRouter


def set_basic_router(
    util: LabelUtil,
    router: APIRouter,
) -> APIRouter:
    """labelに対応したCRUD APIの基本的な定義."""
    ListParam.api(router, lambda: util.find_all().to_model(), "list")
    RemoveParam.api(router, util.delete, "delete")
    CompleteParam.api(
        router,
        lambda pref_uid: util.complete(pref_uid=pref_uid).to_model(),
        "complete",
    )
    return router
