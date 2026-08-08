"""クイズ学習の進捗ユースケース."""

from collections.abc import Iterable

from tanbun.feature.domain.types import UUIDy
from tanbun.feature.quiz.domain.parts import QuizType
from tanbun.feature.quiz.learning.progress.domain import (
    QuizTypeLearningStatus,
    ResourceLearningStatus,
)
from tanbun.feature.quiz.learning.progress.repo import (
    fetch_attempt_rate,
    fetch_coverage,
    fetch_performance,
)


async def fetch_learning_status(
    resource_id: UUIDy,
    user_id: UUIDy,
    quiz_types: Iterable[QuizType] | None = None,
) -> ResourceLearningStatus:
    """QuizTypeごとの指標とリソース全体の学習状況を取得."""
    if quiz_types is None:
        quiz_types = QuizType

    by_quiz_type = {}
    for quiz_type in quiz_types:
        by_quiz_type[quiz_type] = QuizTypeLearningStatus(
            coverage=await fetch_coverage(resource_id, user_id, quiz_type),
            attempt_rate=await fetch_attempt_rate(resource_id, user_id, quiz_type),
            performance=await fetch_performance(resource_id, user_id, quiz_type),
        )
    return ResourceLearningStatus(
        resource_id=resource_id,
        user_id=user_id,
        by_quiz_type=by_quiz_type,
    )
