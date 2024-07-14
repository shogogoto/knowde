"""人物."""
from __future__ import annotations

from knowde._feature._shared.domain.domain import Entity
from knowde.feature.person.domain.lifedate import LifeSpan  # noqa: TCH001


class Person(Entity, frozen=True):
    """人物."""

    name: str
    lifespan: LifeSpan
