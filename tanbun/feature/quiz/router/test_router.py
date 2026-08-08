"""quiz router test."""

import pytest
from fastapi import status
from httpx import AsyncClient

from tanbun.conftest import async_fixture, mark_async_test
from tanbun.feature.domain.types import to_uuid
from tanbun.feature.quiz.candidate.types import CandidateType
from tanbun.feature.quiz.chain.domain import QuizChain, QuizChainRole
from tanbun.feature.quiz.domain.domain import ReadableQuiz
from tanbun.feature.quiz.domain.parts import QuizType
from tanbun.feature.quiz.fixture import fx_u
from tanbun.feature.quiz.router.params import CreateQuizParam
from tanbun.feature.tanbun.label import LSentence
from tanbun.feature.user.label import LUser
from tanbun.feature.user.testing import aauth_header

u = async_fixture()(fx_u)


@mark_async_test()
async def test_sent2term(ac: AsyncClient, u: LUser):
    """単文から用語を当てるクイズの一連の流れ."""
    sent = await LSentence.nodes.first(val="ccc")
    p = CreateQuizParam(
        target_sent_uid=sent.uid,
        quiz_type=QuizType.SENT2TERM,
        cand_type=CandidateType.NEAR,
        n_option=4,
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
    chain = QuizChain.model_validate(res.json())
    ans = chain.answers[0]
    assert ans.is_correct
    assert [quiz.quiz_id for quiz in chain.quizzes] == [rq.quiz_id]
    assert {
        link.sentence_id for link in chain.links if link.role is QuizChainRole.CORRECT
    } == {to_uuid(uid) for uid in rq.correct}
    # 不正解
    res = await ac.post(
        f"/quiz/answer/{rq.quiz_id}",
        json={"selected": rq.distractors},
        headers=h,
    )
    chain = QuizChain.model_validate(res.json())
    ans = chain.answers[0]
    assert not ans.is_correct
    assert ans.who == to_uuid(u.uid)


@pytest.mark.parametrize("quiz_type", [QuizType.REL2PAIR, QuizType.PAIR2REL])
@mark_async_test()
async def test_create_relation_quiz(
    ac: AsyncClient,
    u: LUser,
    quiz_type: QuizType,
):
    """対象単文と関係先を指定して関係クイズを作成する."""
    target = await LSentence.nodes.first(val="ccc")
    pair = await LSentence.nodes.first(val="parent")
    param = CreateQuizParam(
        target_sent_uid=target.uid,
        correct_sent_uids=[pair.uid],
        quiz_type=quiz_type,
        cand_type=CandidateType.ALL,
        n_option=3,
    )

    response = await ac.post(
        "/quiz",
        json=param.model_dump(),
        headers=await aauth_header(email=u.email),
    )

    quiz = ReadableQuiz.model_validate(response.json())
    assert len(quiz.options) == param.n_option
    assert len(quiz.correct) == 1
    if quiz_type is QuizType.REL2PAIR:
        assert quiz.options[quiz.correct[0]] == "parent"

    invalid = param.model_dump()
    invalid["correct_sent_uids"] = []
    response = await ac.post(
        "/quiz",
        json=invalid,
        headers=await aauth_header(email=u.email),
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
