"""リソース学習状況のテスト."""

import pytest

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.namespace import fetch_namespace
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.domain import QuizFillStrategy
from knowde.integration.quiz.learning.fixture import fx_learning
from knowde.integration.quiz.learning.usecase import (
    fetch_learning_status,
    generate_quizzes,
)
from knowde.integration.quiz.repo.answer import create_answer
from knowde.shared.user.label import LUser

u = async_fixture()(fx_learning)


@mark_async_test()
async def test_fetch_learning_status(u: LUser):  # noqa: PLR0914
    """QuizType別の内訳とリソース全体の指標を取得."""
    ns = await fetch_namespace(u.uid)
    rid = ns.resources[0].uid
    n_term2sent = 2
    n_sent2term = 1

    term2sent = await generate_quizzes(
        rid,
        u.uid,
        QuizType.TERM2SENT,
        QuizFillStrategy.IMPORTANCE,
        CandidateType.ALL,
        n_quiz=n_term2sent,
        n_option=3,
    )
    sent2term = await generate_quizzes(
        rid,
        u.uid,
        QuizType.SENT2TERM,
        QuizFillStrategy.IMPORTANCE,
        CandidateType.ALL,
        n_quiz=n_sent2term,
        n_option=3,
    )
    correct = term2sent[0].to_readable()
    incorrect = sent2term[0].to_readable()
    await create_answer(correct.quiz_id, correct.correct, u.uid)
    last_answer = await create_answer(
        incorrect.quiz_id,
        [incorrect.distractors[0]],
        u.uid,
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
