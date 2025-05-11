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
    StructuredRel,
    UniqueIdProperty,
    ZeroOrOne,
)

from knowde.primitive.__core__.nxutil.edge_type import EdgeType


class LHead(StructuredNode):
    """見出し."""

    __label__ = "Head"
    val = StringProperty(index=True, required=True)  # , max_length=MAX_CHARS)
    children = RelationshipTo("LHead", "HEAD")
    parent = RelationshipFrom("LHead", "HEAD", cardinality=One)
    resource = RelationshipTo("LResource", "")


class RelTO(StructuredRel):  # noqa: D101
    pass


class RelRESOLVED(StructuredRel):  # noqa: D101
    pass


class RelBELOW(StructuredRel):  # noqa: D101
    pass


class RelSIBLING(StructuredRel):  # noqa: D101
    pass


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

    # cypher_query で relからNodeのpropertyを取得するために必要
    # resolve_object=Trueにするとpropertiesが空にならずにマッピングされる
    premise = RelationshipFrom("LSentence", EdgeType.TO.name, model=RelTO)
    conculusion = RelationshipTo("LSentence", EdgeType.TO.name, model=RelTO)
    refer = RelationshipFrom("LSentence", EdgeType.RESOLVED.name, model=RelRESOLVED)
    referred = RelationshipTo("LSentence", EdgeType.RESOLVED.name, model=RelRESOLVED)
    parent = RelationshipFrom("LSentence", EdgeType.BELOW.name, model=RelBELOW)
    detail = RelationshipTo("LSentence", EdgeType.BELOW.name, model=RelBELOW)

    sibling = RelationshipTo("LSentence", EdgeType.SIBLING.name, model=RelSIBLING)


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
