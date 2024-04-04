from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID  # noqa: TCH003

from neomodel import DoesNotExist
from pydantic import BaseModel

from knowde._feature._shared.domain import Entity
from knowde._feature._shared.errors.domain import (
    CompleteMultiHitError,
    CompleteNotFoundError,
    NeomodelNotFoundError,
)

from .base import LBase
from .label import Label, Labels

L = TypeVar("L", bound=LBase)
M = TypeVar("M", bound=Entity)


class LabelUtil(BaseModel, Generic[L, M], frozen=True):
    """neomodelを隠蔽する."""

    label: type[L]
    model: type[M]

    def to_neolabel(self, model: M) -> L:
        return self.label(**model.model_dump())

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

    def find_by_id(self, uid: UUID) -> Label[L, M]:
        try:
            lb = self.label.nodes.get(uid=uid.hex)
            return self.to_label(lb)
        except DoesNotExist as e:
            raise NeomodelNotFoundError(msg=str(e)) from e

    def find(self, **kwargs) -> Labels[L, M]:  # noqa: ANN003
        """TODO:pagingが未実装."""
        ls = self.label.nodes.filter(**kwargs)
        return self.to_labels(ls)

    def find_one(self, **kwargs) -> Label[L, M]:  # noqa: ANN003
        lb = self.find_one_or_none(**kwargs)
        if lb is None:
            raise NeomodelNotFoundError
        return lb

    def find_one_or_none(self, **kwargs) -> Label[L, M] | None:  # noqa: ANN003
        lb = self.label.nodes.get_or_none(**kwargs)
        if lb is None:
            return None
        return self.to_label(lb)

    def delete(self, uid: UUID) -> None:
        # 存在チェックはしない
        # 構成要素にrelationshipが含まれるようなmodelでは
        # Label.to_model()が失敗するため用途が限定されるのを避ける
        self.find_by_id(uid).label.delete()

    def create(self, **kwargs) -> Label[L, M]:  # noqa: ANN003
        saved = self.label(**kwargs).save()
        return self.to_label(saved)

    def change(self, uid: UUID, **kwargs) -> Label[L, M]:  # noqa: ANN003
        lb = self.find_by_id(uid).label
        for k, v in kwargs.items():
            if v is not None:
                setattr(lb, k, v)
        if any(kwargs.values()):  # どれか１つでも変更した場合
            return self.to_label(lb.save())
        return self.to_label(lb)
