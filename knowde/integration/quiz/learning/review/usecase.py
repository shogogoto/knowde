"""クイズの復習推薦ユースケース."""

from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.domain import QuizSource
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.fill.usecase import generate_quizzes
from knowde.integration.quiz.learning.review.domain import (
    PreparedReviewQuiz,
    ReviewQuizKind,
)
from knowde.integration.quiz.learning.review.repo import (
    fetch_unattempted_quiz_ids,
)
from knowde.integration.quiz.learning.selection.domain import QuizFillStrategy
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.shared.types import UUIDy


async def prepare_review_quizzes(  # noqa: PLR0917
    resource_id: UUIDy,
    user_id: UUIDy,
    quiz_type: QuizType,
    candidate_type: CandidateType,
    n_quiz: int,
    n_option: int,
) -> list[QuizSource]:
    """既存の未回答クイズを優先し、不足分を復習用に新規生成."""
    prepared = await prepare_review_quizzes_with_reason(
        resource_id,
        user_id,
        quiz_type,
        candidate_type,
        n_quiz,
        n_option,
    )
    return [item.quiz for item in prepared]


async def prepare_review_quizzes_with_reason(  # noqa: PLR0917
    resource_id: UUIDy,
    user_id: UUIDy,
    quiz_type: QuizType,
    candidate_type: CandidateType,
    n_quiz: int,
    n_option: int,
    *,
    generate_missing: bool = True,
) -> list[PreparedReviewQuiz]:
    """既存未回答と低正答率から生成したクイズを根拠付きで返す."""
    unattempted_ids = await fetch_unattempted_quiz_ids(
        resource_id,
        user_id,
        quiz_type,
        limit=n_quiz,
    )
    existing = await restore_quiz_sources(unattempted_ids)
    prepared_existing = [
        PreparedReviewQuiz(quiz=quiz, kind=ReviewQuizKind.UNATTEMPTED)
        for quiz in existing
    ]
    n_missing = n_quiz - len(existing)
    if n_missing == 0 or not generate_missing:
        return prepared_existing

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
    return [
        *prepared_existing,
        *[
            PreparedReviewQuiz(quiz=quiz, kind=ReviewQuizKind.LOW_ACCURACY)
            for quiz in generated
        ],
    ]
