"""復習推薦のテスト."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.namespace import fetch_namespace
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.domain import (
    QuizFillStrategy,
    QuizTargetOrder,
    QuizTargetPool,
)
from knowde.integration.quiz.learning.fixture import fx_learning
from knowde.integration.quiz.learning.repo import (
    fetch_target_ids,
    fetch_unattempted_quiz_ids,
)
from knowde.integration.quiz.learning.usecase import (
    generate_quizzes,
    prepare_review_quizzes,
)
from knowde.integration.quiz.repo.answer import create_answer
from knowde.shared.user.label import LUser

u = async_fixture()(fx_learning)


@mark_async_test()
async def test_fetch_review_target_ids(u: LUser):
    """回答済み単文を低正答率順で復習対象にする."""
    ns = await fetch_namespace(u.uid)
    rid = ns.resources[0].uid
    sources = await generate_quizzes(
        rid,
        u.uid,
        QuizType.TERM2SENT,
        QuizFillStrategy.IMPORTANCE,
        CandidateType.ALL,
        n_quiz=3,
        n_option=3,
    )
    correct_source = sources[0]
    incorrect_source = sources[1]
    correct = correct_source.to_readable()
    incorrect = incorrect_source.to_readable()

    await create_answer(correct.quiz_id, correct.correct, u.uid)
    await create_answer(
        incorrect.quiz_id,
        [incorrect.distractors[0]],
        u.uid,
    )

    targets = await fetch_target_ids(
        rid,
        u.uid,
        QuizType.TERM2SENT,
        QuizTargetPool.COVERED,
        QuizTargetOrder.LOW_ACCURACY,
        limit=3,
    )

    assert targets == [
        incorrect_source.target_id,
        correct_source.target_id,
    ]


@mark_async_test()
async def test_prepare_review_quizzes(u: LUser):
    """既存の未回答クイズを優先し、不足分だけ新規生成."""
    ns = await fetch_namespace(u.uid)
    rid = ns.resources[0].uid
    sources = await generate_quizzes(
        rid,
        u.uid,
        QuizType.TERM2SENT,
        QuizFillStrategy.IMPORTANCE,
        CandidateType.ALL,
        n_quiz=3,
        n_option=3,
    )
    correct_source, incorrect_source, unattempted = sources
    correct = correct_source.to_readable()
    incorrect = incorrect_source.to_readable()
    await create_answer(correct.quiz_id, correct.correct, u.uid)
    await create_answer(
        incorrect.quiz_id,
        [incorrect.distractors[0]],
        u.uid,
    )

    unattempted_ids = await fetch_unattempted_quiz_ids(
        rid,
        u.uid,
        QuizType.TERM2SENT,
        limit=3,
    )
    assert unattempted_ids == [unattempted.quiz_id]

    n_review = 2
    reviews = await prepare_review_quizzes(
        rid,
        u.uid,
        QuizType.TERM2SENT,
        CandidateType.ALL,
        n_quiz=n_review,
        n_option=3,
    )

    assert len(reviews) == n_review
    assert reviews[0].quiz_id == unattempted.quiz_id
    assert reviews[1].quiz_id not in {quiz.quiz_id for quiz in sources}
    assert reviews[1].target_id == incorrect_source.target_id
