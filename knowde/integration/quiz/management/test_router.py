"""Quiz管理APIのテスト."""

from fastapi import status
from httpx import AsyncClient

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.collections import ReadableQuizResult
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.generation.repo import generate_quiz
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser
from knowde.shared.user.testing import aauth_header, aregister

u = async_fixture()(fx_u)


@mark_async_test()
async def test_list_and_delete_created_quizzes_api(ac: AsyncClient, u: LUser):
    """自分が作成したQuizを一覧し、削除できる."""
    target = LSentence.nodes.first(val="ccc")
    own = await generate_quiz(
        QuizType.TERM2SENT,
        CandidateType.ALL,
        target.uid,
        3,
        u.uid,
    )
    other = await aregister(email="quiz-management-api-other@ex.com")
    other_quiz = await generate_quiz(
        QuizType.TERM2SENT,
        CandidateType.ALL,
        target.uid,
        3,
        other.uid,
    )
    headers = await aauth_header(email=u.email)

    response = await ac.get("/quiz/created", headers=headers)
    result = ReadableQuizResult.model_validate(response.json())

    assert [quiz.quiz_id for quiz in result.data.root] == [own.quiz_id]

    response = await ac.delete(f"/quiz/{other_quiz.quiz_id}", headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = await ac.delete(f"/quiz/{own.quiz_id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = await ac.get("/quiz/created", headers=headers)
    result = ReadableQuizResult.model_validate(response.json())
    assert result.total == 0
