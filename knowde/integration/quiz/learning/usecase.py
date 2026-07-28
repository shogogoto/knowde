"""クイズ学習のユースケース."""

from collections.abc import Iterable

from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.domain import QuizSource
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.domain import (
    QuizFillStrategy,
    QuizTypeLearningStatus,
    ResourceLearningStatus,
)
from knowde.integration.quiz.learning.repo import (
    fetch_attempt_rate,
    fetch_coverage,
    fetch_performance,
    fetch_target_ids,
    fetch_unattempted_quiz_ids,
)
from knowde.integration.quiz.repo.create import generate_quiz
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.shared.types import UUIDy


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


async def generate_quizzes(  # noqa: PLR0917
    resource_id: UUIDy,
    user_id: UUIDy,
    quiz_type: QuizType,
    strategy: QuizFillStrategy,
    candidate_type: CandidateType,
    n_quiz: int,
    n_option: int,
    *,
    exclude_target_ids: Iterable[UUIDy] | None = None,
) -> list[QuizSource]:
    """戦略に従って対象を選び、複数のクイズを生成."""
    if not quiz_type.has_term:
        msg = f"{quiz_type}の正解単文の自動選択は未実装です"
        raise NotImplementedError(msg)

    pool, order = strategy.target_selection
    target_ids = await fetch_target_ids(
        resource_id,
        user_id,
        quiz_type,
        pool,
        order,
        limit=n_quiz,
        exclude_sent_ids=exclude_target_ids,
    )
    quizzes = []
    for target_id in target_ids:
        quiz = await generate_quiz(
            quiz_type,
            candidate_type,
            target_id,
            n_option,
            user_id,
        )
        quizzes.append(quiz)
    return quizzes


async def prepare_review_quizzes(  # noqa: PLR0917
    resource_id: UUIDy,
    user_id: UUIDy,
    quiz_type: QuizType,
    candidate_type: CandidateType,
    n_quiz: int,
    n_option: int,
) -> list[QuizSource]:
    """既存の未回答クイズを優先し、不足分を復習用に新規生成."""
    unattempted_ids = await fetch_unattempted_quiz_ids(
        resource_id,
        user_id,
        quiz_type,
        limit=n_quiz,
    )
    existing = await restore_quiz_sources(unattempted_ids)
    n_missing = n_quiz - len(existing)
    if n_missing == 0:
        return existing

    generated = await generate_quizzes(
        resource_id,
        user_id,
        quiz_type,
        QuizFillStrategy.REVIEW,
        candidate_type,
        n_quiz=n_missing,
        n_option=n_option,
        exclude_target_ids=[quiz.target_id for quiz in existing],
    )
    return [*existing, *generated]
