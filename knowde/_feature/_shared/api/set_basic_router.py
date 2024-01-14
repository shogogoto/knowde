from __future__ import annotations

from inspect import signature
from typing import TYPE_CHECKING, Callable, NamedTuple, TypeAlias
from uuid import UUID  # noqa: TCH003

from fastapi import APIRouter, status
from makefun import create_function
from pydantic import BaseModel

from knowde._feature._shared.domain import DomainModel
from knowde._feature._shared.repo.util import LabelUtil  # noqa: TCH001

from .basic_param import (
    CompleteParam,
    ListParam,
    RemoveParam,
)

if TYPE_CHECKING:
    from knowde._feature._shared.endpoint import Endpoint


RouterHook: TypeAlias = Callable[
    [
        type[BaseModel],
        type[DomainModel],
        str,
    ],
    None,
]


class RouterHooks(NamedTuple):
    create_add: RouterHook
    create_change: RouterHook


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

    # hooksの型引数によるAPI定義ではundefined errorが発生した
    # create_fucntionでrouterに渡す関数のSignatureを上書きすれば、
    # エラーが回避できる? できた
    def _define(f: Callable) -> Callable:
        return create_function(signature(f), f)

    def create_add(
        t_in: type[BaseModel],
        t_out: type[DomainModel] = util.model,
        relative: str = "",
    ) -> None:
        def _add(p: t_in) -> t_out:
            return util.create(**p.model_dump()).to_model()

        router.post(
            relative,
            status_code=status.HTTP_201_CREATED,
        )(
            # _define(_add),
            # ハードコードしないとAPI生成時にエラー
            create_function(signature(_add), _add),
        )

    def create_change(
        t_in: type[BaseModel],
        t_out: type[DomainModel] = util.model,
        relative: str = "/{uid}",
    ) -> None:
        def _ch(uid: UUID, p: t_in) -> t_out:
            lb = util.find_one(uid).label
            for k, v in p.model_dump().items():
                if v is not None:
                    setattr(lb, k, v)
            return t_out.to_model(lb.save())

        router.put(
            relative,
        )(
            create_function(signature(_ch), _ch),
        )

    return router, RouterHooks(
        create_add=create_add,
        create_change=create_change,
    )
