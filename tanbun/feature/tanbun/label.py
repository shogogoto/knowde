"""単文のNeo4j label定義."""

from __future__ import annotations

from neomodel import (
    AsyncOne,
    AsyncRelationshipFrom,
    AsyncRelationshipManager,
    AsyncRelationshipTo,
    AsyncStructuredNode,
    AsyncZeroOrOne,
    FloatProperty,
    FulltextIndex,
    StringProperty,
    UniqueIdProperty,
)

from tanbun.feature.domain.graph.edge_type import EdgeType


class LSentence(AsyncStructuredNode):
    """1文."""

    __label__ = "Sentence"
    uid = UniqueIdProperty()
    val = StringProperty(
        index=True,
        required=True,
        fulltext_index=FulltextIndex(),
    )  # , max_length=MAX_CHARS)
    term = AsyncRelationshipTo("LTerm", "TERM", cardinality=AsyncZeroOrOne)
    # 各文からlocationを取得しようとしたが、探索に時間がかかりすぎるのか応答しなくなった
    # 探索コストを削減するために、元からIDを持たせる
    resource_uid = StringProperty(require=True, index=True)  # 作成ユーザーID

    # resource = RelationshipFrom(LResource, "BELOW")

    # cypher_query で relからNodeのpropertyを取得するために必要
    # resolve_object=Trueにするとpropertiesが空にならずにマッピングされる
    premise = AsyncRelationshipFrom("LSentence", EdgeType.TO.name)
    conculusion = AsyncRelationshipTo("LSentence", EdgeType.TO.name)
    refer = AsyncRelationshipFrom("LSentence", EdgeType.RESOLVED.name)
    referred = AsyncRelationshipTo("LSentence", EdgeType.RESOLVED.name)
    parent = AsyncRelationshipFrom("LSentence", EdgeType.BELOW.name)
    detail = AsyncRelationshipTo("LSentence", EdgeType.BELOW.name)
    sibling = AsyncRelationshipTo("LSentence", EdgeType.SIBLING.name)


class LTerm(AsyncStructuredNode):
    """用語."""

    __label__ = "Term"
    uid = UniqueIdProperty()
    val = StringProperty(
        index=True,
        required=True,
        fulltext_index=FulltextIndex(),
    )  # , max_length=MAX_CHARS)
    alias = AsyncRelationshipTo("LTerm", "ALIAS", cardinality=AsyncZeroOrOne)
    sentence: AsyncRelationshipManager = AsyncRelationshipTo("LSentence", "DEF")


class LQuoterm(AsyncStructuredNode):
    """引用用語."""

    __label__ = "Quoterm"
    uid = UniqueIdProperty()
    val = StringProperty(index=True, required=True)
    term: AsyncRelationshipManager = AsyncRelationshipTo(
        "LTerm",
        "QUOTE",
        cardinality=AsyncOne,
    )
    resource_uid = StringProperty(require=True, index=True)  # 作成ユーザーID


class LInterval(AsyncStructuredNode):
    """時刻期間."""

    __label__ = "Interval"
    val = StringProperty(index=True, required=True)
    start = FloatProperty(default=None, index=True)
    end = FloatProperty(default=None, index=True)
