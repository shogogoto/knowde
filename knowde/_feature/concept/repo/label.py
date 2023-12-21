"""neo4j label."""
from __future__ import annotations

from neomodel import (
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
)

from knowde._feature._shared import LBase
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.concept.domain.domain import Concept

L = "Concept"
CLASS_NAME = f"L{L}"


class LConcept(LBase):
    """neo4j label."""

    __label__ = L
    explain = StringProperty()

    src = RelationshipTo(CLASS_NAME, "refer")
    dest = RelationshipFrom(CLASS_NAME, "refer")


util_concept = LabelUtil(label=LConcept, model=Concept)
