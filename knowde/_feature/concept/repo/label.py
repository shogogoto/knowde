"""neo4j label."""
from __future__ import annotations

from typing import TYPE_CHECKING

from neomodel import (
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
)

from knowde._feature._shared import LBase
from knowde._feature._shared.repo.util import RepoUtil
from knowde._feature.concept.domain.domain import Concept

if TYPE_CHECKING:
    from uuid import UUID

L = "Concept"
CLASS_NAME = f"L{L}"


class LConcept(LBase):
    """neo4j label."""

    __label__ = L
    explain = StringProperty()

    src = RelationshipTo(CLASS_NAME, "refer")
    dest = RelationshipFrom(CLASS_NAME, "refer")


util = RepoUtil(label=LConcept, model=Concept)


def to_model(label: LConcept) -> Concept:
    """Db mapper to domain model."""
    return util.to_model(label)


def list_by_pref_uid(pref_uid: str) -> list[LConcept]:
    """uidの前方一致で検索."""
    return util.suggest(pref_uid)


def complete_concept(pref_uid: str) -> Concept:
    """uuidが前方一致する要素を1つ返す."""
    return util.complete(pref_uid)


def find_one_(uid: UUID) -> LConcept:
    """neomodelエラーをラップする."""
    return util.find_one(uid)
