"""labels."""
from __future__ import annotations

from neomodel import (
    ArrayProperty,
    DateTimeFormatProperty,
    One,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    StructuredRel,
    UniqueIdProperty,
    ZeroOrOne,
)


class LResource(StructuredNode):
    """情報源 rootの見出し(H1)."""

    __label__ = "Resource"
    uid = UniqueIdProperty()
    title = StringProperty(index=True, required=True)
    authors = ArrayProperty(StringProperty())
    published = DateTimeFormatProperty(default=None)
    urls = ArrayProperty(StringProperty())


# sentence -[:TERM {alias}]-> (:Term) -[:TERM]-> (:Term) -> ...
class RTerm(StructuredRel):
    """用語."""

    alias = StringProperty(default=None)


class LSentence(StructuredNode):
    """1文."""

    __label__ = "Sentence"
    uid = UniqueIdProperty()
    val = StringProperty(index=True, required=True)  # , max_length=MAX_CHARS)
    term = RelationshipTo("LTerm", "TERM", cardinality=ZeroOrOne, model=RTerm)


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
