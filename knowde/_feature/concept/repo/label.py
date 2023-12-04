"""neo4j label."""
from __future__ import annotations

from typing import TYPE_CHECKING

from neomodel import (
    DateTimeProperty,
    DoesNotExist,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
)

from knowde._feature._shared.timeutil import jst_now
from knowde._feature.concept.domain.domain import Concept
from knowde._feature.concept.error import (
    CompleteMultiHitError,
    CompleteNotFoundError,
    NeomodelNotFoundError,
)

if TYPE_CHECKING:
    from uuid import UUID

L = "Concept"
ClASS_NAME = f"L{L}"


class LConcept(StructuredNode):
    """neo4j label."""

    __label__ = L
    uid = UniqueIdProperty()
    name = StringProperty()
    explain = StringProperty()
    created = DateTimeProperty()
    updated = DateTimeProperty()

    src = RelationshipTo(ClASS_NAME, "refer")
    dest = RelationshipFrom(ClASS_NAME, "refer")

    def pre_save(self) -> None:
        """Set updated datetime now."""
        now = jst_now()
        if self.created is None:
            self.created = now
        self.updated = now


def to_model(label: LConcept) -> Concept:
    """Db mapper to domain model."""
    return Concept.model_validate(label.__properties__)


def list_by_pref_uid(pref_uid: str) -> list[LConcept]:
    """uidの前方一致で検索."""
    return LConcept.nodes.filter(uid__startswith=pref_uid.replace("-", ""))


def complete_concept(pref_uid: str) -> Concept:
    """uuidが前方一致する要素を1つ返す."""
    ls = list_by_pref_uid(pref_uid)
    if len(ls) == 0:
        msg = "ヒットしませんでした."
        raise CompleteNotFoundError(msg)
    if len(ls) > 1:
        uids = [e.uid for e in ls]
        msg = f"{uids}がヒットしました.1件がヒットするように入力桁を増やしてみてね"
        raise CompleteMultiHitError(msg)
    return to_model(ls[0])


def find_one_(uid: UUID) -> LConcept:
    """neomodelエラーをラップする."""
    try:
        return LConcept.nodes.get(uid=uid.hex)
    except DoesNotExist as e:
        raise NeomodelNotFoundError(msg=str(e)) from e
