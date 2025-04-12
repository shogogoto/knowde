"""sysnet DB IO.

folderと一体化したCRUD
permission指定できるよう拡張
"""

from __future__ import annotations

from neomodel import (
    FloatProperty,
    One,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
    ZeroOrOne,
)


class LHead(StructuredNode):
    """見出し."""

    __label__ = "Head"
    val = StringProperty(index=True, required=True)  # , max_length=MAX_CHARS)
    children = RelationshipTo("LHead", "HEAD")
    parent = RelationshipFrom("LHead", "HEAD", cardinality=One)
    resource = RelationshipTo("LResource", "")


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
    alias = RelationshipTo("LTerm", "ALIAS", cardinality=ZeroOrOne)


class LInterval(StructuredNode):
    """時刻期間."""

    __label__ = "Interval"
    val = StringProperty(index=True, required=True)
    start = FloatProperty(default=None, index=True)
    end = FloatProperty(default=None, index=True)
