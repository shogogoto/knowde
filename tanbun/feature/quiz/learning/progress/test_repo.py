"""クイズ学習の進捗repoのテスト."""

import pytest

from tanbun.conftest import async_fixture, mark_async_test
from tanbun.feature.quiz.candidate.types import CandidateType
from tanbun.feature.quiz.domain.parts import QuizType
from tanbun.feature.quiz.generation.repo import generate_quiz
from tanbun.feature.quiz.learning.fixture import (
    fx_learning,
    learning_resource_id,
)
from tanbun.feature.quiz.learning.progress.domain import QuizCoverage
from tanbun.feature.quiz.learning.progress.repo import fetch_coverage
from tanbun.feature.tanbun.label import LSentence
from tanbun.feature.user.label import LUser
from tanbun.feature.user.testing import aregister

u = async_fixture()(fx_learning)


@mark_async_test()
async def test_fetch_coverage(u: LUser):
    """別タイプ・別ユーザーのクイズを除外してcoverageを取得."""
    rid = await learning_resource_id(u.uid)
    target = await LSentence.nodes.first(val="a")
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
