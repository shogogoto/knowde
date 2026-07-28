"""クイズ成績のテスト."""

import pytest

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.namespace import fetch_namespace
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.domain import QuizFillStrategy, QuizPerformance
from knowde.integration.quiz.learning.fixture import fx_learning
from knowde.integration.quiz.learning.repo import fetch_performance
from knowde.integration.quiz.learning.usecase import generate_quizzes
from knowde.integration.quiz.repo.answer import create_answer
from knowde.shared.user.label import LUser

u = async_fixture()(fx_learning)


@mark_async_test()
async def test_fetch_performance(u: LUser):
    """全回答から回答数、正解数、正答率、最終回答日時を取得."""
    ns = await fetch_namespace(u.uid)
    rid = ns.resources[0].uid
    sources = await generate_quizzes(
        rid,
        u.uid,
        QuizType.TERM2SENT,
        QuizFillStrategy.IMPORTANCE,
        CandidateType.ALL,
        n_quiz=1,
        n_option=3,
    )
    quiz = sources[0].to_readable()

    before = await fetch_performance(rid, u.uid, QuizType.TERM2SENT)
    assert before.attempts == 0
    assert before.corrects == 0
    assert before.accuracy == 0
    assert before.last_attempted_at is None

    await create_answer(quiz.quiz_id, quiz.correct, u.uid)
    await create_answer(quiz.quiz_id, [quiz.distractors[0]], u.uid)
    last_answer = await create_answer(quiz.quiz_id, quiz.correct, u.uid)

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
