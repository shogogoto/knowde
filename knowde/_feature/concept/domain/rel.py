"""relation domain."""
from __future__ import annotations

from enum import Enum

from knowde._feature.concept.domain.domain import Concept


class AdjacentConcept(Concept, frozen=True):
    """with connected concepts."""

    sources: list[Concept]
    dests: list[Concept]

    def flatten(self) -> list[ConnectedConcept]:
        """To list with connection type."""
        return [
            ConnectedConcept.model_validate(
                {"conn_type": ConnectionType.Source} | s.model_dump(),
            )
            for s in self.sources
        ] + [
            ConnectedConcept.model_validate(
                {"conn_type": ConnectionType.Destination} | d.model_dump(),
            )
            for d in self.dests
        ]


class ConnectionType(Enum):
    Source = "src"
    Destination = "dest"


class _ConnectedMixin:
    """for field ordering."""

    conn_type: ConnectionType


class ConnectedConcept(Concept, _ConnectedMixin, frozen=True):
    """connected concept."""
