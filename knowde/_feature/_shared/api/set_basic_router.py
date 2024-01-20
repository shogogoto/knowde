from __future__ import annotations

from inspect import signature
from typing import TYPE_CHECKING, NamedTuple, Protocol
from uuid import UUID  # noqa: TCH003

from fastapi import APIRouter, status
from makefun import create_function
from neomodel import db

from knowde._feature._shared.integrated_interface.basic_method import (
    create_basic_methods,
)
from knowde._feature._shared.integrated_interface.generate import (
    create_request_generator,
)
from knowde._feature._shared.integrated_interface.types import CompleteParam
from knowde._feature._shared.repo.util import LabelUtil  # noqa: TCH001

if TYPE_CHECKING:
    from pydantic import BaseModel

    from knowde._feature._shared.domain import DomainModel
    from knowde._feature._shared.endpoint import Endpoint


def create_router(ep: Endpoint) -> APIRouter:
    return APIRouter(
        prefix=f"/{ep.value}",
        tags=[f"/{ep.single_form}"],
    )


class RouterHook(Protocol):
    def __call__(
        self,
        t_in: type[BaseModel],
        t_out: type[DomainModel] | None = None,
        relative: str = "",
    ) -> None:
        ...


class RouterHooks(NamedTuple):
    create_add: RouterHook
    create_change: RouterHook


def set_basic_router(  # noqa: C901
    util: LabelUtil,
    router: APIRouter,
) -> tuple[APIRouter, RouterHooks]:
    """labelに対応したCRUD APIの基本的な定義."""

    def create_add(
        t_in: type[BaseModel],
        t_out: type[DomainModel] | None = None,
        relative: str = "",
    ) -> None:
        if t_out is None:
            t_out = util.model

        def _add(p: t_in) -> t_out:
            with db.transaction:
                return util.create(**p.model_dump()).to_model()

        router.post(
            relative,
            status_code=status.HTTP_201_CREATED,
        )(
            # hooksの型引数によるAPI定義ではundefined errorが発生した
            # create_fucntionでrouterに渡す関数のSignatureを上書きすれば、
            # エラーが回避できる? できた
            create_function(signature(_add), _add),
        )

    def create_change(
        t_in: type[BaseModel],
        t_out: type[DomainModel] | None = None,
        relative: str = "/{uid}",
    ) -> None:
        if t_out is None:
            t_out = util.model

        def _ch(uid: UUID, p: t_in) -> t_out:
            with db.transaction:
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

    def create_delete() -> None:
        def _rm(uid: UUID) -> None:
            with db.transaction:
                util.delete(uid)

        router.delete(
            "/{uid}",
            status_code=status.HTTP_204_NO_CONTENT,
            response_model=None,
        )(
            create_function(signature(_rm), _rm),
        )

    methods = create_basic_methods(util)
    _ = create_request_generator(
        router,
        CompleteParam,
        util.model,
        methods.complete,
        relative="/completion",
    )

    _ = create_request_generator(
        router,
        None,
        list[util.model],
        methods.ls,
    )

    create_delete()
    return router, RouterHooks(
        create_add,
        create_change,
    )
