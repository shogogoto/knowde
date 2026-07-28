"""クイズ回答率のテスト."""

import pytest

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.namespace import fetch_namespace
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.domain import QuizFillStrategy
from knowde.integration.quiz.learning.fixture import fx_learning
from knowde.integration.quiz.learning.repo import fetch_attempt_rate
from knowde.integration.quiz.learning.usecase import generate_quizzes
from knowde.integration.quiz.repo.answer import create_answer
from knowde.shared.user.label import LUser

u = async_fixture()(fx_learning)


@mark_async_test()
async def test_fetch_attempt_rate(u: LUser):
    """複数回答しても回答済みクイズを重複して数えない."""
    ns = await fetch_namespace(u.uid)
    rid = ns.resources[0].uid
    n_quiz = 2
    quizzes = await generate_quizzes(
        rid,
        u.uid,
        QuizType.TERM2SENT,
        QuizFillStrategy.IMPORTANCE,
        CandidateType.ALL,
        n_quiz=n_quiz,
        n_option=3,
    )

    before = await fetch_attempt_rate(rid, u.uid, QuizType.TERM2SENT)
    assert before.available == n_quiz
    assert before.attempted == 0
    assert before.ratio == 0

    quiz = quizzes[0].to_readable()
    await create_answer(quiz.quiz_id, quiz.correct, u.uid)
    await create_answer(quiz.quiz_id, quiz.correct, u.uid)

    after = await fetch_attempt_rate(rid, u.uid, QuizType.TERM2SENT)
    assert after.available == n_quiz
    assert after.attempted == 1
    assert after.ratio == pytest.approx(after.attempted / after.available)
