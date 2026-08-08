"""クイズ成績のテスト."""

import pytest

from tanbun.conftest import async_fixture, mark_async_test
from tanbun.feature.quiz.domain.parts import QuizType
from tanbun.feature.quiz.learning.fixture import (
    answer_test_quiz,
    fx_learning,
    generate_test_quizzes,
    learning_resource_id,
)
from tanbun.feature.quiz.learning.progress.domain import QuizPerformance
from tanbun.feature.quiz.learning.progress.repo import fetch_performance
from tanbun.feature.user.label import LUser

u = async_fixture()(fx_learning)


@mark_async_test()
async def test_fetch_performance(u: LUser):
    """全回答から回答数、正解数、正答率、最終回答日時を取得."""
    rid = await learning_resource_id(u.uid)
    quiz = (await generate_test_quizzes(rid, u.uid, 1))[0]

    before = await fetch_performance(rid, u.uid, QuizType.TERM2SENT)
    assert before.attempts == 0
    assert before.corrects == 0
    assert before.accuracy == 0
    assert before.last_attempted_at is None

    await answer_test_quiz(quiz, u.uid, correctly=True)
    await answer_test_quiz(quiz, u.uid, correctly=False)
    last_answer = await answer_test_quiz(quiz, u.uid, correctly=True)

    expected = QuizPerformance(
        resource_id=rid,
        user_id=u.uid,
        quiz_type=QuizType.TERM2SENT,
        attempts=3,
        corrects=2,
        last_attempted_at=last_answer.created,
    )
    after = await fetch_performance(rid, u.uid, expected.quiz_type)
    assert after == expected
    assert after.accuracy == pytest.approx(after.corrects / after.attempts)
