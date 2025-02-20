"""labels."""
from __future__ import annotations

from neomodel import (
    DateProperty,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
)


class LResource(StructuredNode):
    """情報源."""

    __label__ = "Resource"
    uid = UniqueIdProperty()
    title = StringProperty(index=True)
    published = DateProperty(default=None)


class LSentence(StructuredNode):
    """1文."""

    __label__ = "Sentence"
    uid = UniqueIdProperty()
    val = StringProperty(index=True)  # , max_length=MAX_CHARS)
    terms = RelationshipTo("LTerm", "NAME")


class LTerm(StructuredNode):
    """用語."""

    __label__ = "Term"
    uid = UniqueIdProperty()
    val = StringProperty(index=True)  # , max_length=MAX_CHARS)


class LHead(StructuredNode):
    """見出し."""

    __label__ = "Head"
    val = StringProperty(index=True)  # , max_length=MAX_CHARS)
