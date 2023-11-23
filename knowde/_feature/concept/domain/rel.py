"""relation domain."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from .domain import Concept


class ConceptAdjacent(BaseModel, frozen=True):
    """with connected concepts."""

    center: Concept
    sources: list[Concept]
    dests: list[Concept]


class ConnectionType(Enum):
    Source = "src"
    Destination = "dest"


class ConnectedConcept(Concept, frozen=True):
    """connected concept."""

    conn_type: ConnectionType
