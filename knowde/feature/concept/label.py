"""neo4j label."""


from neomodel import StringProperty, StructuredNode, UniqueIdProperty


class Concept(StructuredNode):
    """neo4j label."""

    uid = UniqueIdProperty()
    name = StringProperty()
    explain = StringProperty()
