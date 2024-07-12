from knowde._feature._shared.domain.domain import Entity


class Location(Entity, frozen=True):
    """位置."""

    name: str
