from __future__ import annotations

from knowde.core.domain.domain import Entity


class Location(Entity, frozen=True):
    """位置."""

    name: str

    @property
    def output(self) -> str:
        return f"{self.name}({self.valid_uid})"
