from __future__ import annotations

from typing import Generic, TypeVar

from neomodel import (
    RelationshipFrom,
    RelationshipManager,
    RelationshipTo,
    ZeroOrMore,
)
from pydantic import BaseModel

from .base import LBase, RelBase

S = TypeVar("S", bound=LBase)
T = TypeVar("T", bound=LBase)
R = TypeVar("R", bound=RelBase)


class RelUtil(
    BaseModel,
    Generic[S, T, R],
    frozen=True,
    arbitrary_types_allowed=True,
):
    """関係先を紐付ける.

    以下のためにStructuredNodeとは切り離して関数化した.
    - StructuredNodeにRelPropertyをつけると他のStructuredNodeと依存して
      パッケージの独立性が侵される
    - neomodelのtypingを補完する
    """

    t_source: type[S]
    t_target: type[T]
    name: str
    t_rel: type[R]
    cardinality: type[RelationshipManager] = ZeroOrMore

    def to(
        self,
        source: S,
    ) -> RelationshipManager:
        return RelationshipTo(
            cls_name=self.t_target,
            relation_type=self.name,
            cardinality=ZeroOrMore,
            model=self.t_rel,  # StructuredRel
        ).build_manager(source, name="")  # nameが何に使われているのか不明

    def from_(self, target: T) -> RelationshipManager:
        return RelationshipFrom(
            cls_name=self.t_source,
            relation_type=self.name,
            cardinality=self.cardinality,
            model=self.t_rel,  # StructuredRel
        ).build_manager(target, name="")  # nameが何に使われているのか不明

    def connect(self, s: S, t: T) -> R:
        return self.to(s).connect(t).save()
