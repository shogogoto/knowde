"""relation domain."""
from __future__ import annotations

from enum import Enum
from typing import Self
from uuid import UUID  # noqa: TCH003

from pydantic import model_validator

from knowde._feature.concept.domain.domain import ChangeProp, Concept


class AdjacentConcept(Concept, frozen=True):
    """with connected concepts."""

    srcs: list[Concept]
    dests: list[Concept]

    def flatten(self) -> list[ConnectedConcept]:
        """To list with connection type."""
        return [
            ConnectedConcept.model_validate(
                {"conn_type": ConnectionType.Source} | s.model_dump(),
            )
            for s in self.srcs
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


class SourceProp(ChangeProp, frozen=True):
    source_id: UUID | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.source_id is None and self.name is None:
            msg = "Idまたはnameを入力してください"
            raise ValueError(msg)
        return self


class DestinationProp(ChangeProp, frozen=True):
    destination_id: UUID | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.destination_id is None and self.name is None:
            msg = "Idまたはnameを入力してください"
            raise ValueError(msg)
        return self
