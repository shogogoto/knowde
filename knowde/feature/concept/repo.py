"""concept repository."""
from __future__ import annotations

from knowde.feature.concept.label import Concept


def list_concepts() -> list[Concept]:
    """List concepts."""
    return Concept.nodes
