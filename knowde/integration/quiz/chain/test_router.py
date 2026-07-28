"""QuizChain APIのテスト."""

from httpx import AsyncClient
from starlette import status

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.chain.domain import QuizChain
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.generation.repo import generate_quiz
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser
from knowde.shared.user.testing import aauth_header, aregister

u = async_fixture()(fx_u)


@mark_async_test()
async def test_expand_quiz_and_sentence_chain_api(ac: AsyncClient, u: LUser):
    """選択したQuizとSentenceをAPIから1ホップずつ展開."""
    target = LSentence.nodes.first(val="ccc")
    quiz = await generate_quiz(
        QuizType.TERM2SENT,
        CandidateType.ALL,
        target.uid,
        5,
        u.uid,
    )
    headers = await aauth_header(email=u.email)

    response = await ac.get(
        f"/quiz/chain/quizzes/{quiz.quiz_id}",
        headers=headers,
    )
    quiz_chain = QuizChain.model_validate(response.json())
    assert [item.quiz_id for item in quiz_chain.quizzes] == [quiz.quiz_id]

    response = await ac.get(
        f"/quiz/chain/sentences/{target.uid}",
        headers=headers,
    )
    sentence_chain = QuizChain.model_validate(response.json())
    assert [item.quiz_id for item in sentence_chain.quizzes] == [quiz.quiz_id]
    assert len(sentence_chain.sentences) == 1


@mark_async_test()
async def test_reject_other_users_quiz_chain_api(ac: AsyncClient, u: LUser):
    """他ユーザーだけがLEARNするQuizはAPIから取得できない."""
    target = LSentence.nodes.first(val="ccc")
    other = await aregister(email="quiz-chain-api-other@ex.com")
    quiz = await generate_quiz(
        QuizType.TERM2SENT,
        CandidateType.ALL,
        target.uid,
        5,
        other.uid,
    )

    response = await ac.get(
        f"/quiz/chain/quizzes/{quiz.quiz_id}",
        headers=await aauth_header(email=u.email),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
