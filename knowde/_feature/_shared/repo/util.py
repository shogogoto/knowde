from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from neomodel import DoesNotExist
from pydantic import BaseModel

from knowde._feature._shared.domain import DomainModel
from knowde._feature._shared.errors.domain import (
    CompleteMultiHitError,
    CompleteNotFoundError,
    NeomodelNotFoundError,
)

from .label import LBase

if TYPE_CHECKING:
    from uuid import UUID

L = TypeVar("L", bound=LBase)
M = TypeVar("M", bound=DomainModel)


class RepoUtil(BaseModel, Generic[L, M], frozen=True):
    label: type[L]
    model: type[M]

    def to_model(self, label: L) -> M:
        return self.model.model_validate(label.__properties__)

    def suggest(self, pref_uid: str) -> list[L]:
        pref_hex = pref_uid.replace("-", "")
        return self.label.nodes.filter(uid__startswith=pref_hex)

    def complete(self, pref_uid: str) -> M:
        ls = self.suggest(pref_uid)
        if len(ls) == 0:
            msg = "ヒットしませんでした."
            raise CompleteNotFoundError(msg)
        if len(ls) > 1:
            uids = [e.uid for e in ls]
            msg = f"{uids}がヒットしました.1件がヒットするように入力桁を増やしてみてね"
            raise CompleteMultiHitError(msg)
        return self.to_model(ls[0])

    def find_one(self, uid: UUID) -> L:
        try:
            return self.label.nodes.get(uid=uid.hex)
        except DoesNotExist as e:
            raise NeomodelNotFoundError(msg=str(e)) from e
