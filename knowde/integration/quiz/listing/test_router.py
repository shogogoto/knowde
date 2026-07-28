"""クイズ・回答一覧APIのテスト."""

from httpx import AsyncClient

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.answering.repo import create_answer
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.answer import Answers
from knowde.integration.quiz.domain.collections import ReadableQuizResult
from knowde.integration.quiz.domain.domain import QuizSource
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.generation.repo import generate_quiz
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser
from knowde.shared.user.testing import aauth_header

u = async_fixture()(fx_u)


async def _generate_quizzes(u: LUser, count: int) -> list[QuizSource]:
    """一覧API用のクイズを生成."""
    target = LSentence.nodes.first(val="ccc")
    return [
        await generate_quiz(
            QuizType.TERM2SENT,
            CandidateType.ALL,
            target.uid,
            3,
            u.uid,
        )
        for _ in range(count)
    ]


@mark_async_test()
async def test_list_learning_quizzes_api(ac: AsyncClient, u: LUser):
    """学習対象クイズをページングして取得."""
    quizzes = await _generate_quizzes(u, 3)
    headers = await aauth_header(email=u.email)
    page_size = 2

    response = await ac.get(
        "/quiz",
        params={"page": 1, "size": page_size},
        headers=headers,
    )
    result = ReadableQuizResult.model_validate(response.json())

    assert result.total == len(quizzes)
    assert len(result.data.root) == page_size


@mark_async_test()
async def test_list_own_answers_api(ac: AsyncClient, u: LUser):
    """指定クイズに対する認証ユーザー自身の回答を取得."""
    quiz = (await _generate_quizzes(u, 1))[0].to_readable()
    correct = await create_answer(quiz.quiz_id, quiz.correct, u.uid)
    wrong = await create_answer(quiz.quiz_id, [quiz.distractors[0]], u.uid)

    response = await ac.get(
        f"/quiz/answer/{quiz.quiz_id}",
        headers=await aauth_header(email=u.email),
    )
    answers = Answers.model_validate(response.json())

    assert {answer.answer_uid for answer in answers.root} == {
        correct.answer_uid,
        wrong.answer_uid,
    }
