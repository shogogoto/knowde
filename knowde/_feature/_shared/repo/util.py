from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID  # noqa: TCH003

from neomodel import DoesNotExist
from pydantic import BaseModel

from knowde._feature._shared.domain import DomainModel
from knowde._feature._shared.errors.domain import (
    CompleteMultiHitError,
    CompleteNotFoundError,
    NeomodelNotFoundError,
)

from .base import LBase
from .label import Label, Labels

L = TypeVar("L", bound=LBase)
M = TypeVar("M", bound=DomainModel)


class LabelUtil(BaseModel, Generic[L, M], frozen=True):
    """neomodelを隠蔽する."""

    label: type[L]
    model: type[M]

    def to_label(self, label: L) -> Label[L, M]:
        return Label(label=label, model=self.model)

    def to_labels(self, labels: list[L]) -> Labels[L, M]:
        return Labels(root=labels, model=self.model)

    def suggest(self, pref_uid: str) -> Labels[L, M]:
        pref_hex = pref_uid.replace("-", "")
        lbs = self.label.nodes.filter(uid__startswith=pref_hex)
        return self.to_labels(lbs)

    def complete(self, pref_uid: str) -> Label[L, M]:
        lbs = self.suggest(pref_uid)
        n = len(lbs)
        if n == 0:
            msg = "ヒットしませんでした."
            raise CompleteNotFoundError(msg)
        if n > 1:
            uids = [e.uid for e in lbs]
            msg = f"{n}件ヒット.入力桁を増やしてみてね.{uids}"
            raise CompleteMultiHitError(msg)
        return self.to_label(lbs[0])

    def find_one(self, uid: UUID) -> Label[L, M]:
        try:
            lb = self.label.nodes.get(uid=uid.hex)
            return self.to_label(lb)
        except DoesNotExist as e:
            raise NeomodelNotFoundError(msg=str(e)) from e

    def find_all(self) -> Labels[L, M]:
        """TODO:pagingが未実装."""
        ls = self.label.nodes.all()
        return self.to_labels(ls)

    def delete(self, uid: UUID) -> None:
        self.find_one(uid).label.delete()

    def create(self, **kwargs) -> Label[L, M]:  # noqa: ANN003
        saved = self.label(**kwargs).save()
        return self.to_label(saved)
