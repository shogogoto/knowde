"""復習推薦のテスト."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.quiz.candidate.types import CandidateType
from knowde.feature.quiz.domain.parts import QuizType
from knowde.feature.quiz.learning.fixture import (
    answer_test_quiz,
    fx_learning,
    generate_test_quizzes,
    learning_resource_id,
)
from knowde.feature.quiz.learning.review.repo import (
    fetch_unattempted_quiz_ids,
)
from knowde.feature.quiz.learning.review.usecase import (
    prepare_review_quizzes,
)
from knowde.feature.quiz.learning.selection.domain import (
    QuizTargetOrder,
    QuizTargetPool,
)
from knowde.feature.quiz.learning.selection.repo import fetch_target_ids
from knowde.feature.user.label import LUser

u = async_fixture()(fx_learning)


@mark_async_test()
async def test_fetch_review_target_ids(u: LUser):
    """回答済み単文を低正答率順で復習対象にする."""
    rid = await learning_resource_id(u.uid)
    sources = await generate_test_quizzes(rid, u.uid, 3)
    correct_source = sources[0]
    incorrect_source = sources[1]

    await answer_test_quiz(correct_source, u.uid, correctly=True)
    await answer_test_quiz(incorrect_source, u.uid, correctly=False)

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
    rid = await learning_resource_id(u.uid)
    sources = await generate_test_quizzes(rid, u.uid, 3)
    correct_source, incorrect_source, unattempted = sources
    await answer_test_quiz(correct_source, u.uid, correctly=True)
    await answer_test_quiz(incorrect_source, u.uid, correctly=False)

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
