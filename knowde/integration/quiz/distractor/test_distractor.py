"""誤答肢test."""

from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.distractor.distractor import (
    MAX_RELATION_PATH_CANDIDATES,
    fetch_distractor_ids,
    fetch_pair2rel_distractor_ids,
)
from knowde.integration.quiz.domain.rel import QuizRel
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


@mark_async_test()
async def test_limit_pair2rel_path_candidates(monkeypatch: pytest.MonkeyPatch):
    """大きなresourceでもPAIR2RELの最短path探索数を制限する."""
    candidates = [UUID(int=index) for index in range(1, 1001)]
    correct_id = UUID(int=2000)
    inspected_ids = []

    def fake_fetch_paths(target_id, candidate_ids):
        inspected_ids.extend(candidate_ids)
        return {correct_id: [QuizRel.PREMISE]}

    monkeypatch.setattr(
        "knowde.integration.quiz.distractor.distractor._fetch_relation_paths",
        AsyncMock(side_effect=fake_fetch_paths),
    )
    candidate_type = SimpleNamespace(fetch=AsyncMock(return_value=candidates))

    with pytest.raises(InsufficientOptionsError):
        await fetch_pair2rel_distractor_ids(
            UUID(int=3000),
            candidate_type,
            n_distractor=1,
            correct_ids=[correct_id],
        )

    assert len(inspected_ids) == MAX_RELATION_PATH_CANDIDATES + 1
