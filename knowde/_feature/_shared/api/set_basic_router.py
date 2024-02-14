from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, Protocol
from uuid import UUID

from fastapi import APIRouter
from neomodel import db

from knowde._feature._shared.integrated_interface.generate_req import (
    APIRequests,
    inject_signature,
)
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


def set_basic_router(
    util: LabelUtil,
    router: APIRouter,
) -> tuple[APIRouter, RouterHooks]:
    """labelに対応したCRUD APIの基本的な定義."""
    reqs = APIRequests(router=router)

    def create_add(
        t_in: type[BaseModel],
    ) -> None:
        def _add(p: t_in) -> util.model:
            with db.transaction:
                return util.create(**p.model_dump()).to_model()

        reqs.post(inject_signature(_add, [t_in], util.model))

    def create_change(
        t_in: type[BaseModel],
    ) -> None:
        def _ch(uid: UUID, p: t_in) -> util.model:
            with db.transaction:
                lb = util.find_one(uid).label
                for k, v in p.model_dump().items():
                    if v is not None:
                        setattr(lb, k, v)
                return util.model.to_model(lb.save())

        reqs.put(inject_signature(_ch, [UUID, t_in], util.model))

    def _rm(uid: UUID) -> None:
        with db.transaction:
            util.delete(uid)

    def _complete(pref_uid: str) -> util.model:
        return util.complete(pref_uid).to_model()

    def _ls() -> list[util.model]:
        return util.find_all().to_model()

    reqs.delete(inject_signature(_rm, [UUID]))
    reqs.get(inject_signature(_complete, [str], util.model), "/completion")
    reqs.get(inject_signature(_ls, [], list[util.model]))

    return router, RouterHooks(
        create_add,
        create_change,
    )
