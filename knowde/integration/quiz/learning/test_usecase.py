"""クイズ学習ユースケースのテスト."""

import pytest

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.resource.repo.owner import check_entry_owner
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.domain import QuizFillStrategy
from knowde.integration.quiz.learning.fixture import (
    answer_test_quiz,
    fx_learning,
    generate_test_quizzes,
    learning_resource_id,
)
from knowde.integration.quiz.learning.repo import fetch_coverage, fetch_performance
from knowde.shared.user.label import LUser
from knowde.shared.user.testing import aregister

u = async_fixture()(fx_learning)


@pytest.mark.parametrize(
    "strategy",
    [
        QuizFillStrategy.IMPORTANCE,
        QuizFillStrategy.COVERAGE,
    ],
)
@mark_async_test()
async def test_generate_quizzes(
    u: LUser,
    strategy: QuizFillStrategy,
):
    """戦略に従って未クイズ化単文から指定件数のクイズを生成."""
    rid = await learning_resource_id(u.uid)
    n_quiz = 2

    before = await fetch_coverage(rid, u.uid, QuizType.TERM2SENT)
    quizzes = await generate_test_quizzes(
        rid,
        u.uid,
        n_quiz,
        strategy=strategy,
    )
    after = await fetch_coverage(rid, u.uid, QuizType.TERM2SENT)

    assert before.covered == 0
    assert len(quizzes) == n_quiz
    assert len({quiz.target_id for quiz in quizzes}) == n_quiz
    assert after.covered == n_quiz
    assert after.ratio == pytest.approx(n_quiz / after.eligible)


@mark_async_test()
async def test_generate_and_answer_quiz_from_another_users_resource(u: LUser):
    """他人のリソースから自分用クイズを生成して回答する."""
    rid = await learning_resource_id(u.uid)
    learner = await aregister(email="other-resource-learner@ex.com")
    assert await check_entry_owner(u.uid, rid)
    assert not await check_entry_owner(learner.uid, rid)

    quiz = (await generate_test_quizzes(rid, learner.uid, 1))[0]

    owner_coverage = await fetch_coverage(rid, u.uid, QuizType.TERM2SENT)
    learner_coverage = await fetch_coverage(
        rid,
        learner.uid,
        QuizType.TERM2SENT,
    )
    assert owner_coverage.covered == 0
    assert learner_coverage.covered == 1

    answer = await answer_test_quiz(quiz, learner.uid, correctly=True)
    learner_performance = await fetch_performance(
        rid,
        learner.uid,
        QuizType.TERM2SENT,
    )
    owner_performance = await fetch_performance(
        rid,
        u.uid,
        QuizType.TERM2SENT,
    )
    assert answer.is_correct
    assert learner_performance.attempts == 1
    assert learner_performance.corrects == 1
    assert owner_performance.attempts == 0
