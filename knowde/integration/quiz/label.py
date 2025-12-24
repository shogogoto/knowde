"""neomodel label."""

from neomodel import (
    ArrayProperty,
    AsyncOne,
    AsyncRelationshipManager,
    AsyncRelationshipTo,
    AsyncStructuredNode,
    BooleanProperty,
    DateTimeProperty,
    StringProperty,
    UniqueIdProperty,
)

from knowde.integration.quiz.domain.domain import QuizType


class LQuiz(AsyncStructuredNode):
    """クイズ.

    ここの情報だけから問題を生成できる
    """

    __label__ = "Quiz"
    uid = UniqueIdProperty()
    statement_type = StringProperty(required=True, choices=QuizType)
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
    option: AsyncRelationshipManager = AsyncRelationshipTo(  # type: ignore  # noqa: PGH003
        "LSentence",
        "QUIZ_OPTION",
    )


class LAnswer(AsyncStructuredNode):
    """回答."""

    __label__ = "Answer"
    uid = UniqueIdProperty()
    created = DateTimeProperty()
    is_corrent = BooleanProperty()  # 正答 or not
    selected_ids = ArrayProperty()
