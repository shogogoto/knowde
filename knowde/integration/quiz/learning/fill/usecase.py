"""学習用クイズの補充ユースケース."""

from collections.abc import Iterable

from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.domain import QuizSource
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.selection.domain import QuizFillStrategy
from knowde.integration.quiz.learning.selection.repo import fetch_target_ids
from knowde.integration.quiz.repo.create import generate_quiz
from knowde.shared.types import UUIDy


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
