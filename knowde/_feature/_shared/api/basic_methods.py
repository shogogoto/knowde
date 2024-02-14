from __future__ import annotations

from typing import TYPE_CHECKING

from neomodel import db
from pydantic_partial.partial import create_partial_model

from knowde._feature._shared.api.types import Add, BasicMethods, Change
from knowde._feature._shared.repo.util import LabelUtil  # noqa: TCH001

if TYPE_CHECKING:
    from uuid import UUID

    from pydantic import BaseModel


def create_basic_methods(util: LabelUtil) -> BasicMethods:
    def rm(uid: UUID) -> None:
        with db.transaction:
            util.delete(uid)

    def complete(pref_uid: str) -> util.model:
        return util.complete(pref_uid).to_model()

    def ls() -> list[util.model]:
        return util.find_all().to_model()

    return BasicMethods(
        rm,
        complete,
        ls,
    )


def create_add_and_change(
    util: LabelUtil,
    t_in: type[BaseModel],
) -> tuple[Add, Change, type]:
    """引数の型注入をするためにbasic methodsとは別の扱い."""

    def add(p: t_in) -> util.model:
        with db.transaction:
            return util.create(**p.model_dump()).to_model()

    Opt = create_partial_model(t_in)  # noqa: N806

    def ch(uid: UUID, p: Opt) -> util.model:
        with db.transaction:
            lb = util.find_one(uid).label
            for k, v in p.model_dump().items():
                if v is not None:
                    setattr(lb, k, v)
            return util.model.to_model(lb.save())

    return add, ch, Opt
