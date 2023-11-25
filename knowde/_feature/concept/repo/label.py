"""neo4j label."""
from neomodel import (
    DateTimeProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
)

from knowde._feature._shared.timeutil import jst_now
from knowde._feature.concept.domain.domain import Concept

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
