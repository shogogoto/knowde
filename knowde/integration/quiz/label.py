"""neomodel label."""

from neomodel import (
    AsyncOne,
    AsyncRelationshipManager,
    AsyncRelationshipTo,
    AsyncStructuredNode,
    BooleanProperty,
    DateTimeProperty,
    UniqueIdProperty,
)


class LQuiz(AsyncStructuredNode):
    """クイズ."""

    __label__ = "Quiz"
    uid = UniqueIdProperty()
    # リンク切れ状態を明示して壊れたことが分かるようにして再構成を促す
    is_link_broken = BooleanProperty(default=False)
    created = DateTimeProperty()

    # 単文ネットワークを中心としているので用語を指すつもりであっても、その単文を指すべし
    target: AsyncRelationshipManager = AsyncRelationshipTo(  # type: ignore  # noqa: PGH003
        "LSentence",
        "QUIZ_TARGET",
        cardinality=AsyncOne,
    )

    # 誤答肢を指す
    ditract: AsyncRelationshipManager = AsyncRelationshipTo(  # type: ignore  # noqa: PGH003
        "LSentence",
        "DITRACT",
    )
