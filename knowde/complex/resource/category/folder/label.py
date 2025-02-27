"""neomodel label."""
from neomodel import RelationshipTo, StringProperty, StructuredNode, ZeroOrOne


class LFolder(StructuredNode):
    """sysnetの入れ物."""

    __label__ = "Folder"
    name = StringProperty(index=True)

    parent = RelationshipTo("LFolder", "PARENT", cardinality=ZeroOrOne)
    owner = RelationshipTo("LUser", "OWNED", cardinality=ZeroOrOne)
