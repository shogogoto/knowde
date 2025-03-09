"""neomodel label."""

from neomodel import (
    AliasProperty,
    ArrayProperty,
    DateTimeNeo4jFormatProperty,
    RelationshipManager,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
    ZeroOrOne,
)

from knowde.complex.resource.category.folder import MFolder, MResource
from knowde.primitive.user.repo import LUser


class LEntry(StructuredNode):
    """情報源とその容れ物の同一視."""

    __abstract_node__ = True
    __label__ = "Entry"
    uid = UniqueIdProperty()

    owner: RelationshipManager = RelationshipTo(
        LUser,
        "OWNED",
        cardinality=ZeroOrOne,
    )

    parent: RelationshipManager = RelationshipTo(
        "LFolder",
        "PARENT",
        cardinality=ZeroOrOne,
    )


class LResource(LEntry):
    """情報源 rootの見出し(H1)."""

    __label__ = "Resource"
    title = StringProperty(index=True, required=True)
    name = AliasProperty("title")
    authors = ArrayProperty(StringProperty())
    published = DateTimeNeo4jFormatProperty(default=None)
    urls = ArrayProperty(StringProperty())
    # txthash

    @property
    def frozen(self) -> MResource:
        """hashableへ."""
        return MResource(
            name=self.name,
            element_id_property=self.element_id,
            uid=self.uid,
            authors=self.authors,
            published=self.published,
            urls=self.urls,
        )


class LFolder(LEntry):
    """sysnetの入れ物."""

    __label__ = "Folder"
    name = StringProperty(index=True)

    @property
    def frozen(self) -> MFolder:
        """hashableへ."""
        return MFolder(
            name=self.name,
            element_id_property=self.element_id,
            uid=self.uid,
        )
