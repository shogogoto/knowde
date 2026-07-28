"""quiz router test."""

from httpx import AsyncClient

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.answer import Answer
from knowde.integration.quiz.domain.domain import ReadableQuiz
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.router.params import CreateQuizParam
from knowde.shared.knowde.label import LSentence
from knowde.shared.types import to_uuid
from knowde.shared.user.label import LUser
from knowde.shared.user.testing import aauth_header

u = async_fixture()(fx_u)


@mark_async_test()
async def test_sent2term(ac: AsyncClient, u: LUser):
    """単文から用語を当てるクイズの一連の流れ."""
    sent = LSentence.nodes.first(val="ccc")
    p = CreateQuizParam(
        target_sent_uid=sent.uid,
        quiz_type=QuizType.SENT2TERM,
        cand_type=CandidateType.NEAR,
        n_option=4,
        user_uid=u.uid,
    )

    h = await aauth_header(email=u.email)
    res = await ac.post(
        "/quiz",
        json=p.model_dump(),
        headers=h,
    )
    rq = ReadableQuiz.model_validate(res.json())
    res = await ac.post(
        f"/quiz/answer/{rq.quiz_id}",
        json={"selected": rq.correct},
        headers=h,
    )
    ans = Answer.model_validate(res.json())
    assert ans.is_correct
    # 不正解
    res = await ac.post(
        f"/quiz/answer/{rq.quiz_id}",
        json={"selected": rq.distractors},
        headers=h,
    )
    ans = Answer.model_validate(res.json())
    assert not ans.is_correct
    assert ans.who == to_uuid(u.uid)
