"""学習用クイズの補充ユースケース."""

from collections.abc import Iterable

from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.domain import QuizSource
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.errors import InsufficientOptionsError
from knowde.integration.quiz.generation.repo import generate_quiz
from knowde.integration.quiz.learning.selection.domain import QuizFillStrategy
from knowde.integration.quiz.learning.selection.repo import (
    fetch_target_ids,
    fetch_uncovered_relation_pairs,
)
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
        pairs = await fetch_uncovered_relation_pairs(
            resource_id,
            user_id,
            quiz_type,
            # 生成不能な関係を延々と試すと推薦API全体が遅くなる。
            limit=max(n_quiz * 3, n_quiz),
            exclude_sent_ids=exclude_target_ids,
        )
        quizzes = []
        generated_target_ids: set[UUIDy] = set()
        for target_id, correct_id in pairs:
            if target_id in generated_target_ids:
                continue
            try:
                quiz = await generate_quiz(
                    quiz_type,
                    candidate_type,
                    target_id,
                    n_option,
                    user_id,
                    correct_sent_uids=[correct_id],
                )
            except InsufficientOptionsError:
                continue
            quizzes.append(quiz)
            generated_target_ids.add(target_id)
            if len(quizzes) == n_quiz:
                break
        return quizzes

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
