from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from neomodel import (
    RelationshipFrom,
    RelationshipManager,
    RelationshipTo,
    ZeroOrMore,
)
from pydantic import BaseModel

from knowde._feature._shared.repo.query import query_cypher

from .base import LBase, RelBase

if TYPE_CHECKING:
    from uuid import UUID

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

    def find_by_source_id(self, source_uid: UUID) -> list[R]:
        """Get StructuredRel object."""
        sl, tl = self.labels
        return query_cypher(
            f"""
            MATCH (t:{sl})-[rel:{self.name}]->({tl})
            WHERE t.uid = $uid
            RETURN rel
            """,
            params={"uid": source_uid.hex},
        ).get("rel")

    def find_by_target_id(self, target_uid: UUID) -> list[R]:
        """Get StructuredRel object."""
        sl, tl = self.labels
        return query_cypher(
            f"""
            MATCH (t:{sl})-[rel:{self.name}]->({tl})
            WHERE s.uid = $uid
            RETURN rel
            """,
            params={"uid": target_uid.hex},
        ).get("rel")

    @property
    def labels(self) -> tuple[str, str]:
        """Return source and target labels."""
        return (
            self.t_source.label(),
            self.t_target.label(),
        )
