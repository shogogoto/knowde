"""人物."""
from __future__ import annotations

from knowde._feature._shared.domain.domain import Entity
from knowde.feature.person.domain.lifedate import LifeDate  # noqa: TCH001


class Person(Entity, frozen=True):
    """人物."""

    name: str
    birth: LifeDate | None = None
    death: LifeDate | None = None
