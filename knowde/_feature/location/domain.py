from knowde._feature._shared.domain.domain import Entity


class Location(Entity, frozen=True):
    """位置."""

    name: str

    @property
    def output(self) -> str:
        return f"{self.name}({self.valid_uid})"


# class LocationTree(CompositionTree, frozen=True):
#     pass

# def output(self) ->str:
