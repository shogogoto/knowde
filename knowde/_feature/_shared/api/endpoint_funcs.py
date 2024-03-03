from __future__ import annotations

from typing import TYPE_CHECKING

from neomodel import db
from pydantic import BaseModel
from pydantic_partial.partial import create_partial_model

from knowde._feature._shared.repo.util import LabelUtil  # noqa: TCH001

if TYPE_CHECKING:
    from uuid import UUID

    from knowde._feature._shared.api.types import Add, Change
    from knowde._feature._shared.domain import DomainModel


class EndpointFuncs(BaseModel, frozen=True):
    util: LabelUtil

    def rm(self, uid: UUID) -> None:
        with db.transaction:
            self.util.delete(uid)

    def complete(self, pref_uid: str) -> DomainModel:
        return self.util.complete(pref_uid).to_model()

    def ls(self) -> list[DomainModel]:
        return self.util.find_all().to_model()

    def add_factory(self, t_in: type[BaseModel]) -> Add:
        def add(p: t_in) -> DomainModel:
            with db.transaction:
                return self.util.create(**p.model_dump()).to_model()

        return add

    def ch_factory(self, t_in: type[BaseModel]) -> Change:
        Opt = create_partial_model(t_in)  # noqa: N806

        def change(uid: UUID, p: Opt) -> DomainModel:
            with db.transaction:
                return self.util.change(uid, **p.model_dump()).to_model()

        return change
