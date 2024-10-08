"""domain model."""
from __future__ import annotations

from knowde.core.domain.domain import Entity
from knowde.primitive.location.domain import Location
from knowde.primitive.time.domain.domain import Time


class Event(Entity, frozen=True):
    """出来事."""

    text: str
    when: Time | None = None
    where: Location | None = None

    @property
    def output(self) -> str:
        """Output for cli."""
        return f"{self.text}({self.valid_uid})"
