"""usecase test."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.distractor.domain import SamplingType
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.router.params import CreateQuizParam
from knowde.integration.quiz.router.usecase import create_quiz_uc
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser

u = async_fixture()(fx_u)


@mark_async_test()
async def test_create_quiz_uc(u: LUser):
    """クイズ作成."""
    tgt = LSentence.nodes.first(val="ccc")
    p = CreateQuizParam(
        target_sent_uid=tgt.uid,
        quiz_type=QuizType.TERM2SENT,
        cand_type=CandidateType.NEAR,
        sampling_type=SamplingType.RANDOM,
    )
    res = await create_quiz_uc(p)
    assert len(res.root) == 1
