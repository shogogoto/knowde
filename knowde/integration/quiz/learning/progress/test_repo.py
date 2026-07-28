"""クイズ学習の進捗repoのテスト."""

import pytest

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.fixture import (
    fx_learning,
    learning_resource_id,
)
from knowde.integration.quiz.learning.progress.domain import QuizCoverage
from knowde.integration.quiz.learning.progress.repo import fetch_coverage
from knowde.integration.quiz.repo.create import generate_quiz
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser
from knowde.shared.user.testing import aregister

u = async_fixture()(fx_learning)


@mark_async_test()
async def test_fetch_coverage(u: LUser):
    """別タイプ・別ユーザーのクイズを除外してcoverageを取得."""
    rid = await learning_resource_id(u.uid)
    target = LSentence.nodes.first(val="a")
    expected = QuizCoverage(
        resource_id=rid,
        user_id=u.uid,
        quiz_type=QuizType.TERM2SENT,
        eligible=5,
        covered=0,
    )

    assert await fetch_coverage(rid, u.uid, expected.quiz_type) == expected

    await generate_quiz(
        QuizType.TERM2SENT,
        CandidateType.ALL,
        target.uid,
        3,
        u.uid,
    )
    await generate_quiz(
        QuizType.SENT2TERM,
        CandidateType.ALL,
        target.uid,
        3,
        u.uid,
    )
    other = await aregister(email="quiz2@ex.com")
    await generate_quiz(
        QuizType.TERM2SENT,
        CandidateType.ALL,
        target.uid,
        3,
        other.uid,
    )

    expected = expected.model_copy(update={"covered": 1})
    coverage = await fetch_coverage(rid, u.uid, expected.quiz_type)
    assert coverage == expected
    assert coverage.ratio == pytest.approx(expected.covered / expected.eligible)
