from __future__ import annotations

from inspect import signature
from typing import TYPE_CHECKING, Callable, NamedTuple

from fastapi import APIRouter, status
from makefun import create_function

from knowde._feature._shared.repo.util import LabelUtil  # noqa: TCH001

from .basic_param import (
    CompleteParam,
    ListParam,
    RemoveParam,
)

if TYPE_CHECKING:
    from pydantic import BaseModel

    from knowde._feature._shared.endpoint import Endpoint


class RouterHooks(NamedTuple):
    create_add: Callable[[type[BaseModel]], None]


def create_router(ep: Endpoint) -> APIRouter:
    return APIRouter(
        prefix=f"/{ep.value}",
        tags=[f"/{ep.single_form}"],
    )


def set_basic_router(
    util: LabelUtil,
    router: APIRouter,
) -> tuple[APIRouter, RouterHooks]:
    """labelに対応したCRUD APIの基本的な定義."""
    ListParam.api(router, lambda: util.find_all().to_model(), "list")
    RemoveParam.api(router, util.delete, "delete")
    CompleteParam.api(
        router,
        lambda pref_uid: util.complete(pref_uid=pref_uid).to_model(),
        "complete",
    )

    def create_add(
        t_in: type[BaseModel],
    ) -> None:
        def _add(p: t_in) -> util.model:
            return util.create(**p.model_dump()).to_model()

        router.post(
            "",
            status_code=status.HTTP_201_CREATED,
        )(
            # hooksの型引数によるAPI定義ではundefined errorが発生した
            # create_fucntionでrouterに渡す関数のSignatureを上書きすれば、
            # エラーが回避できる? できた
            create_function(signature(_add), _add),
        )

    # def create_change(
    #     t_in: type[BaseModel],
    # ) -> None:
    #     def _ch(p: t_in) -> util.model:
    #         pass

    return router, RouterHooks(create_add)
