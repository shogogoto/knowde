"""neomodel label."""

from abc import abstractmethod
from typing import override

from neomodel import (
    AliasProperty,
    ArrayProperty,
    AsyncRelationshipManager,
    AsyncRelationshipTo,
    AsyncStructuredNode,
    AsyncZeroOrOne,
    DateProperty,
    DateTimeNeo4jFormatProperty,
    IntegerProperty,
    One,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
)

from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.user.label import LUser  # noqa: F401

from .mapper import Entry, MFolder, MResource


class LHead(StructuredNode):
    """見出し."""

    __label__ = "Head"
    uid = UniqueIdProperty()
    val = StringProperty(index=True, required=True)  # , max_length=MAX_CHARS)
    children = RelationshipTo("LHead", "HEAD")
    parent = RelationshipFrom("LHead", "HEAD", cardinality=One)
    resource = RelationshipFrom("LResource", "HEAD")

    below = RelationshipTo("LSentence", EdgeType.BELOW.name)
    child = RelationshipTo("LHead", EdgeType.HEAD.name)


class LEntry(AsyncStructuredNode):
    """情報源とその容れ物の同一視."""

    __abstract_node__ = True
    __label__ = "Entry"
    uid = UniqueIdProperty()  # parents辿る手間を避けるため

    owner: AsyncRelationshipManager = AsyncRelationshipTo(
        "LUser",
        "OWNED",
        cardinality=AsyncZeroOrOne,
    )

    parent: AsyncRelationshipManager = AsyncRelationshipTo(
        "LFolder",
        "PARENT",
        cardinality=AsyncZeroOrOne,
    )

    @property
    @abstractmethod
    def frozen(self) -> Entry:
        """namespace用hashable."""
        raise NotImplementedError


class LResource(LEntry):
    """情報源 rootの見出し(H1)."""

    __label__ = "Resource"
    title = StringProperty(index=True, required=True)  # userの中でユニーク
    name = AliasProperty("title")
    authors = ArrayProperty(StringProperty())
    published = DateProperty()
    urls = ArrayProperty(StringProperty())

    # file由来
    txt_hash = IntegerProperty()
    updated = DateTimeNeo4jFormatProperty()

    @property
    @override
    def frozen(self) -> MResource:
        return MResource(
            name=self.name,
            element_id_property=self.element_id,
            uid=self.uid,
            authors=self.authors,
            published=self.published,
            urls=self.urls,
            txt_hash=self.txt_hash,
            updated=self.updated,
        )


class LFolder(LEntry):
    """sysnetの入れ物."""

    __label__ = "Folder"
    name = StringProperty(index=True)

    @property
    @override
    def frozen(self) -> MFolder:
        """hashableへ."""
        return MFolder(
            name=self.name,
            element_id_property=self.element_id,
            uid=self.uid,
        )
