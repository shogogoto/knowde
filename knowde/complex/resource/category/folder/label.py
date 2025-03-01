"""neomodel label."""
from functools import cache

from neomodel import (
    RelationshipManager,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    ZeroOrOne,
)

from knowde.complex.resource.category.folder import MFolder
from knowde.primitive.user.repo import LUser


@cache
def to_frozen_cache(name: str, element_id_property: str) -> MFolder:
    """ORMからfrozenへ変換."""
    return MFolder(name=name, element_id_property=element_id_property)


class LFolder(StructuredNode):
    """sysnetの入れ物."""

    __label__ = "Folder"
    name = StringProperty(index=True)

    parent: RelationshipManager = RelationshipTo(
        "LFolder",
        "PARENT",
        cardinality=ZeroOrOne,
    )
    owner: RelationshipManager = RelationshipTo(
        LUser,
        "OWNED",
        cardinality=ZeroOrOne,
    )

    @property
    def frozen(self) -> MFolder:
        """hashableへ."""
        return to_frozen_cache(self.name, self.element_id)
