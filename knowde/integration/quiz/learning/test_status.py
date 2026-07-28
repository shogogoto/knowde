"""リソース学習状況のテスト."""

import pytest

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.fixture import (
    answer_test_quiz,
    fx_learning,
    generate_test_quizzes,
    learning_resource_id,
)
from knowde.integration.quiz.learning.usecase import (
    fetch_learning_status,
)
from knowde.shared.user.label import LUser

u = async_fixture()(fx_learning)


@mark_async_test()
async def test_fetch_learning_status(u: LUser):
    """QuizType別の内訳とリソース全体の指標を取得."""
    rid = await learning_resource_id(u.uid)
    n_term2sent = 2
    n_sent2term = 1

    term2sent = await generate_test_quizzes(
        rid,
        u.uid,
        n_term2sent,
    )
    sent2term = await generate_test_quizzes(
        rid,
        u.uid,
        n_sent2term,
        quiz_type=QuizType.SENT2TERM,
    )
    await answer_test_quiz(term2sent[0], u.uid, correctly=True)
    last_answer = await answer_test_quiz(
        sent2term[0],
        u.uid,
        correctly=False,
    )

    status = await fetch_learning_status(
        rid,
        u.uid,
        [QuizType.TERM2SENT, QuizType.SENT2TERM],
    )
    term_status = status.by_quiz_type[QuizType.TERM2SENT]
    sent_status = status.by_quiz_type[QuizType.SENT2TERM]

    assert term_status.coverage.covered == n_term2sent
    assert term_status.attempt_rate.attempted == 1
    assert term_status.performance.corrects == 1
    assert sent_status.coverage.covered == n_sent2term
    assert sent_status.attempt_rate.attempted == 1
    assert sent_status.performance.corrects == 0

    total_eligible = term_status.coverage.eligible + sent_status.coverage.eligible
    total_covered = n_term2sent + n_sent2term
    total_available = n_term2sent + n_sent2term
    total_attempted = 2
    assert status.overall_coverage == pytest.approx(
        total_covered / total_eligible,
    )
    assert status.overall_attempt_rate == pytest.approx(
        total_attempted / total_available,
    )
    assert status.overall_accuracy == pytest.approx(1 / total_attempted)
    assert status.last_attempted_at == last_answer.created
