"""sysnet DB IO.

folderと一体化したCRUD
permission指定できるよう拡張
"""
from __future__ import annotations

from neomodel import (
    AliasProperty,
    ArrayProperty,
    DateTimeNeo4jFormatProperty,
    One,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
    ZeroOrOne,
)


class LResource(StructuredNode):
    """情報源 rootの見出し(H1)."""

    __label__ = "Resource"
    uid = UniqueIdProperty()
    title = StringProperty(index=True, required=True)
    name = AliasProperty("title")
    authors = ArrayProperty(StringProperty())
    published = DateTimeNeo4jFormatProperty(default=None)
    urls = ArrayProperty(StringProperty())

    heads = RelationshipTo("LHead", "HEAD")


class LSentence(StructuredNode):
    """1文."""

    __label__ = "Sentence"
    uid = UniqueIdProperty()
    val = StringProperty(index=True, required=True)  # , max_length=MAX_CHARS)
    term = RelationshipTo("LTerm", "TERM", cardinality=ZeroOrOne)


class LTerm(StructuredNode):
    """用語."""

    __label__ = "Term"
    uid = UniqueIdProperty()
    val = StringProperty(index=True, required=True)  # , max_length=MAX_CHARS)
    alias = RelationshipTo("LTerm", "TERM", cardinality=ZeroOrOne)


class LHead(StructuredNode):
    """見出し."""

    __label__ = "Head"
    val = StringProperty(index=True, required=True)  # , max_length=MAX_CHARS)
    children = RelationshipTo("LHead", "HEAD")
    parent = RelationshipFrom("LHead", "HEAD", cardinality=One)
