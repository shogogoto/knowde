"""人物."""
from knowde._feature._shared.domain.domain import Entity


class Person(Entity, frozen=True):
    """人物."""

    name: str
