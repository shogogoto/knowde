"""domain model."""
from __future__ import annotations

from knowde._feature.location.domain import Location  # noqa: TCH001
from knowde._feature.time.domain.domain import Time  # noqa: TCH001
from knowde.core.domain.domain import Entity


class Event(Entity, frozen=True):
    """出来事."""

    text: str
    when: Time | None = None
    where: Location | None = None

    @property
    def output(self) -> str:
        """Output for cli."""
        return f"{self.text}({self.valid_uid})"
