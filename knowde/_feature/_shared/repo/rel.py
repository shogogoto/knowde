from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from neomodel import (
    RelationshipFrom,
    RelationshipManager,
    RelationshipTo,
    ZeroOrMore,
)
from pydantic import BaseModel
from typing_extensions import override

from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.concept.error import CompleteMultiHitError, CompleteNotFoundError

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

    @override
    def model_post_init(self, __context: Any) -> None:
        # for add register to db._NODE_CLASS_REGISTRY
        RelationshipTo(
            cls_name=self.t_target,
            relation_type=self.name,
            cardinality=ZeroOrMore,
            model=self.t_rel,  # StructuredRel
        )

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

    def connect(self, s: S, t: T, **kwargs) -> R:  # noqa: ANN003
        rel = self.to(s).connect(t)
        for k, v in kwargs.items():
            setattr(rel, k, v)
        return rel.save()

    def disconnect(self, uid: UUID) -> None:
        sl, tl = self.labels
        query_cypher(
            f"""
            MATCH (:{sl})-[rel:{self.name} {{uid: $uid}}]->(:{tl})
            DELETE rel
            """,
            params={"uid": uid.hex},
        )

    def find_by_source_id(self, source_uid: UUID) -> list[R]:
        """Get StructuredRel object."""
        sl, tl = self.labels
        return query_cypher(
            f"""
            MATCH (:{sl}{{uid: $uid}})-[rel:{self.name}]->(:{tl})
            RETURN rel
            """,
            params={"uid": source_uid.hex},
        ).get("rel")

    def find_by_target_id(self, target_uid: UUID) -> list[R]:
        """Get StructuredRel object."""
        sl, tl = self.labels
        return query_cypher(
            f"""
            MATCH (:{sl})-[rel:{self.name}]->(:{tl}{{uid: $uid}})
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

    def complete(self, pref_uid: str) -> R:
        """関係のuidを前方一致で検索."""
        sl, tl = self.labels
        rels = query_cypher(
            f"""
            MATCH p = (:{sl})-[rel:{self.name}]->(:{tl})
            WHERE rel.uid STARTS WITH $pref_uid
            RETURN rel
            """,
            params={"pref_uid": pref_uid},
        ).get("rel")

        n = len(rels)
        if n == 0:
            msg = "ヒットしませんでした."
            raise CompleteNotFoundError(msg)
        if n > 1:
            msg = f"{n}件ヒット.1つだけヒットするよう入力桁を増やしてみてね."
            raise CompleteMultiHitError(msg)
        return rels[0]

    def find_one_or_none(self, rel_uid: UUID) -> R | None:
        sl, tl = self.labels
        rels = query_cypher(
            f"""
            MATCH (:{sl})-[rel:{self.name} {{uid: $uid}}]->(:{tl})
            RETURN rel
            """,
            params={"uid": rel_uid.hex},
        ).get("rel")

        if len(rels) == 1:
            return rels[0]
        return None
