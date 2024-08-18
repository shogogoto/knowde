"""neomodelの基本操作のwrapper."""
from __future__ import annotations

from typing import Generic, TypeVar
from uuid import UUID  # noqa: TCH003

from neomodel import DoesNotExist
from pydantic import BaseModel

from knowde.core.domain import Entity
from knowde.core.errors.domain import (
    AlreadyExistsError,
    CompleteNotFoundError,
    MultiHitError,
    NeomodelNotFoundError,
)
from knowde.core.label_repo.value_util import NodeUtil

from .base import LBase
from .label import Label, Labels

L = TypeVar("L", bound=LBase)
M = TypeVar("M", bound=Entity)


class LBaseUtil(NodeUtil[L], frozen=True):
    """neomodelの基本操作."""

    t: type[L]

    def suggest(self, pref_uid: str) -> list[L]:
        """UUIDの前方一致による複数個検索."""
        pref_hex = pref_uid.replace("-", "")
        return self.t.nodes.filter(uid__startswith=pref_hex)

    def complete(self, pref_uid: str) -> L:
        """UUIDの前方一致による1つ検索."""
        lbs = self.suggest(pref_uid)
        n = len(lbs)
        if n == 0:
            msg = "ヒットしませんでした."
            raise CompleteNotFoundError(msg)
        if n > 1:
            uids = [e.uid for e in lbs]
            msg = f"{n}件ヒット.入力桁を増やしてみてね.{uids}"
            raise MultiHitError(msg)
        return lbs[0]

    def find_by_id(self, uid: UUID) -> L:  # noqa: D102
        try:
            return self.t.nodes.get(uid=uid.hex)
        except DoesNotExist as e:
            raise NeomodelNotFoundError(msg=str(e)) from e

    def delete_by_uid(self, uid: UUID) -> None:  # noqa: D102
        # 存在チェックはしない
        # 構成要素にrelationshipが含まれるようなmodelでは
        # Label.to_model()が失敗するため用途が限定されるのを避ける
        self.find_by_id(uid).delete()

    def change(self, uid: UUID, **kwargs) -> L:  # noqa: ANN003 D102
        lb = self.find_by_id(uid)
        for k, v in kwargs.items():
            if v is not None:
                setattr(lb, k, v)
        if any(kwargs.values()):  # どれか１つでも変更した場合
            return lb.save()
        return lb


class LabelUtil(BaseModel, Generic[L, M], frozen=True):
    """neomodelを隠蔽する."""

    label: type[L]
    model: type[M]

    @property
    def util(self) -> LBaseUtil:
        """基本操作用インスタンス."""
        return LBaseUtil(t=self.label)

    def to_neolabel(self, model: M) -> L:
        """モデルからneomdel labelへ."""
        return self.label(**model.model_dump())

    def to_label(self, label: L) -> Label[L, M]:
        """モデルにlabel変換を持たせる."""
        return Label(label=label, model=self.model)

    def to_labels(self, labels: list[L]) -> Labels[L, M]:  # noqa: D102
        return Labels(root=labels, model=self.model)

    def suggest(self, pref_uid: str) -> Labels[L, M]:  # noqa: D102
        lbs = self.util.suggest(pref_uid)
        return self.to_labels(lbs)

    def complete(self, pref_uid: str) -> Label[L, M]:  # noqa: D102
        lb = self.util.complete(pref_uid)
        return self.to_label(lb)

    def find_by_id(self, uid: UUID) -> Label[L, M]:  # noqa: D102
        lb = self.util.find_by_id(uid)
        return self.to_label(lb)

    def find(self, **kwargs) -> Labels[L, M]:  # noqa: ANN003
        """TODO:pagingが未実装."""
        return self.to_labels(self.util.find(**kwargs))

    def find_one(self, **kwargs) -> Label[L, M]:  # noqa: ANN003
        """Noneを許容しない."""
        lb = self.util.find_one(**kwargs)
        return self.to_label(lb)

    def find_one_or_none(self, **kwargs) -> Label[L, M] | None:  # noqa: ANN003
        """Noneを許容する."""
        lb = self.util.find_one_or_none(**kwargs)
        if lb is None:
            return None
        return self.to_label(lb)

    def delete(self, uid: UUID) -> None:  # noqa: D102
        self.find_by_id(uid).label.delete()

    def create(self, **kwargs) -> Label[L, M]:  # noqa: ANN003 D102
        saved = self.util.create(**kwargs)
        return self.to_label(saved)

    def change(self, uid: UUID, **kwargs) -> Label[L, M]:  # noqa: ANN003 D102
        lb = self.util.change(uid, **kwargs)
        return self.to_label(lb)

    def new(self, **kwargs) -> Label[L, M]:  # noqa: ANN003
        """新しく作成."""
        lb = self.find_one_or_none(**kwargs)
        if lb is not None:
            msg = f"{kwargs}は既に存在します"
            raise AlreadyExistsError(msg)
        return self.create(**kwargs)

    def fetch(self, **kwargs) -> Label[L, M]:  # noqa: ANN003
        """１つだけ作成。既存があればそれを返す."""
        lb = self.find_one_or_none(**kwargs)
        if lb is not None:
            return lb
        return self.create(**kwargs)
