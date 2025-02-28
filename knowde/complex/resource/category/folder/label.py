"""neomodel label."""
from neomodel import (
    RelationshipManager,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    ZeroOrOne,
)

from knowde.primitive.user.repo import LUser


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
