"""クイズ回答repoのテスト."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.answering.repo import create_answer
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.generation.repo import generate_quiz
from knowde.integration.quiz.listing.repo import list_answers
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser

u = async_fixture()(fx_u)


@mark_async_test()
async def test_create_answer(u: LUser):
    """正解と不正解を保存して回答一覧を返す."""
    target = LSentence.nodes.first(val="ccc")
    source = await generate_quiz(
        QuizType.TERM2SENT,
        CandidateType.ALL,
        target.uid,
        5,
        u.uid,
    )
    quiz = source.to_readable()
    assert (await list_answers([quiz.quiz_id], user_uid=u.uid)).root == []

    correct = await create_answer(quiz.quiz_id, quiz.correct, u.uid)
    incorrect = LSentence.nodes.first(val="todetail")
    wrong = await create_answer(quiz.quiz_id, [incorrect.uid], u.uid)
    answers = await list_answers([quiz.quiz_id], user_uid=u.uid)

    assert correct.is_correct
    assert not wrong.is_correct
    assert {answer.answer_uid for answer in answers.root} == {
        correct.answer_uid,
        wrong.answer_uid,
    }
