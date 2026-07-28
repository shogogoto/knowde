"""誤答肢test."""

import pytest

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.distractor.distractor import fetch_distractor_ids
from knowde.integration.quiz.errors import InsufficientOptionsError
from knowde.integration.quiz.fixture import fx_u
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser

u = async_fixture()(fx_u)


@mark_async_test()
async def test_raise_insufficient_options(u: LUser):
    """候補不足はQuizType共通の公開エラーへ変換する."""
    target = LSentence.nodes.first(val="ccc")

    with pytest.raises(InsufficientOptionsError):
        await fetch_distractor_ids(
            [target.uid],
            CandidateType.ALL,
            n_distractor=10_000,
            must_has_term=False,
        )
