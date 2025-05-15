"""sysnet DB IO.

folderと一体化したCRUD
permission指定できるよう拡張
"""

from __future__ import annotations

from neomodel import (
    FloatProperty,
    FulltextIndex,
    One,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
    ZeroOrOne,
)

from knowde.complex.entry.label import LResource
from knowde.primitive.__core__.nxutil.edge_type import EdgeType


class LHead(StructuredNode):
    """見出し."""

    __label__ = "Head"
    uid = UniqueIdProperty()
    val = StringProperty(index=True, required=True)  # , max_length=MAX_CHARS)
    children = RelationshipTo("LHead", "HEAD")
    parent = RelationshipFrom("LHead", "HEAD", cardinality=One)
    resource = RelationshipFrom(LResource, "HEAD")

    below = RelationshipTo("LSentence", EdgeType.BELOW.name)
    child = RelationshipTo("LHead", EdgeType.HEAD.name)


class LSentence(StructuredNode):
    """1文."""

    __label__ = "Sentence"
    uid = UniqueIdProperty()
    val = StringProperty(
        index=True,
        required=True,
        fulltext_index=FulltextIndex(),
    )  # , max_length=MAX_CHARS)
    term = RelationshipTo("LTerm", "TERM", cardinality=ZeroOrOne)
    resource = RelationshipFrom(LResource, "BELOW")

    # cypher_query で relからNodeのpropertyを取得するために必要
    # resolve_object=Trueにするとpropertiesが空にならずにマッピングされる
    premise = RelationshipFrom("LSentence", EdgeType.TO.name)
    conculusion = RelationshipTo("LSentence", EdgeType.TO.name)
    refer = RelationshipFrom("LSentence", EdgeType.RESOLVED.name)
    referred = RelationshipTo("LSentence", EdgeType.RESOLVED.name)
    parent = RelationshipFrom("LSentence", EdgeType.BELOW.name)
    detail = RelationshipTo("LSentence", EdgeType.BELOW.name)
    sibling = RelationshipTo("LSentence", EdgeType.SIBLING.name)


class LTerm(StructuredNode):
    """用語."""

    __label__ = "Term"
    uid = UniqueIdProperty()
    val = StringProperty(
        index=True,
        required=True,
        fulltext_index=FulltextIndex(),
    )  # , max_length=MAX_CHARS)
    alias = RelationshipTo("LTerm", "ALIAS", cardinality=ZeroOrOne)


class LInterval(StructuredNode):
    """時刻期間."""

    __label__ = "Interval"
    val = StringProperty(index=True, required=True)
    start = FloatProperty(default=None, index=True)
    end = FloatProperty(default=None, index=True)
