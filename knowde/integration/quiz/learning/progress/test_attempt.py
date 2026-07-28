"""クイズ回答率のテスト."""

import pytest

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.fixture import (
    answer_test_quiz,
    fx_learning,
    generate_test_quizzes,
    learning_resource_id,
)
from knowde.integration.quiz.learning.progress.repo import fetch_attempt_rate
from knowde.shared.user.label import LUser

u = async_fixture()(fx_learning)


@mark_async_test()
async def test_fetch_attempt_rate(u: LUser):
    """複数回答しても回答済みクイズを重複して数えない."""
    rid = await learning_resource_id(u.uid)
    n_quiz = 2
    quizzes = await generate_test_quizzes(rid, u.uid, n_quiz)

    before = await fetch_attempt_rate(rid, u.uid, QuizType.TERM2SENT)
    assert before.available == n_quiz
    assert before.attempted == 0
    assert before.ratio == 0

    await answer_test_quiz(quizzes[0], u.uid, correctly=True)
    await answer_test_quiz(quizzes[0], u.uid, correctly=True)

    after = await fetch_attempt_rate(rid, u.uid, QuizType.TERM2SENT)
    assert after.available == n_quiz
    assert after.attempted == 1
    assert after.ratio == pytest.approx(after.attempted / after.available)
