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

from .label import Label, Labels, LBase

if TYPE_CHECKING:
    from uuid import UUID

L = TypeVar("L", bound=LBase)
M = TypeVar("M", bound=DomainModel)


class LabelUtil(BaseModel, Generic[L, M], frozen=True):
    """neomodelを隠蔽する."""

    label: type[L]
    model: type[M]

    def to_model(self, label: L) -> M:
        return self.model.model_validate(label.__properties__)

    def to_label(self, label: L) -> Label[L, M]:
        return Label(label=label, convert=self.to_model)

    def to_labels(self, labels: list[L]) -> Labels[L, M]:
        return Labels(root=labels, convert=self.to_model)

    def suggest(self, pref_uid: str) -> Labels[L, M]:
        pref_hex = pref_uid.replace("-", "")
        lbs = self.label.nodes.filter(uid__startswith=pref_hex)
        return self.to_labels(lbs)

    def complete(self, pref_uid: str) -> Label[L, M]:
        lbs = self.suggest(pref_uid)
        if len(lbs) == 0:
            msg = "ヒットしませんでした."
            raise CompleteNotFoundError(msg)
        if len(lbs) > 1:
            uids = [e.uid for e in lbs]
            msg = f"{uids}がヒットしました.1件がヒットするように入力桁を増やしてみてね"
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

    def create(self, **kwargs: dict) -> Label[L, M]:
        saved = self.label(**kwargs).save()
        return self.to_label(saved)
