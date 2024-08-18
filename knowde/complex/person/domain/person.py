"""人物."""
from __future__ import annotations

from knowde.core.domain.domain import Entity
from knowde.primitive.time.domain.period import Period  # noqa: TCH001


class Person(Entity, frozen=True):
    """人物."""

    name: str
    lifespan: Period

    @property
    def output(self) -> str:
        """Output for cli."""
        ls = self.lifespan.output
        ps = f"{self.name}({self.valid_uid})"
        if ls == "":
            return ps
        return f"{ps} {ls}"
