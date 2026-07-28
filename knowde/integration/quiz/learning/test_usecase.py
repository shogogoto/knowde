"""クイズ学習ユースケースのテスト."""

import pytest

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.namespace import fetch_namespace
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.domain import QuizFillStrategy
from knowde.integration.quiz.learning.fixture import fx_learning
from knowde.integration.quiz.learning.repo import fetch_coverage
from knowde.integration.quiz.learning.usecase import generate_quizzes
from knowde.shared.user.label import LUser

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
    ns = await fetch_namespace(u.uid)
    rid = ns.resources[0].uid
    n_quiz = 2

    before = await fetch_coverage(rid, u.uid, QuizType.TERM2SENT)
    quizzes = await generate_quizzes(
        rid,
        u.uid,
        QuizType.TERM2SENT,
        strategy,
        CandidateType.ALL,
        n_quiz=n_quiz,
        n_option=3,
    )
    after = await fetch_coverage(rid, u.uid, QuizType.TERM2SENT)

    assert before.covered == 0
    assert len(quizzes) == n_quiz
    assert len({quiz.target_id for quiz in quizzes}) == n_quiz
    assert after.covered == n_quiz
    assert after.ratio == pytest.approx(n_quiz / after.eligible)
