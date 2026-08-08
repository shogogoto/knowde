"""クイズ回答repoのテスト."""

from tanbun.conftest import async_fixture, mark_async_test
from tanbun.feature.quiz.answering.repo import create_answer
from tanbun.feature.quiz.candidate.types import CandidateType
from tanbun.feature.quiz.domain.parts import QuizType
from tanbun.feature.quiz.fixture import fx_u
from tanbun.feature.quiz.generation.repo import generate_quiz
from tanbun.feature.quiz.listing.repo import list_answers
from tanbun.feature.tanbun.label import LSentence
from tanbun.feature.user.label import LUser

u = async_fixture()(fx_u)


@mark_async_test()
async def test_create_answer(u: LUser):
    """正解と不正解を保存して回答一覧を返す."""
    target = await LSentence.nodes.first(val="ccc")
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
    incorrect = await LSentence.nodes.first(val="todetail")
    wrong = await create_answer(quiz.quiz_id, [incorrect.uid], u.uid)
    answers = await list_answers([quiz.quiz_id], user_uid=u.uid)

    assert correct.is_correct
    assert not wrong.is_correct
    assert {answer.answer_uid for answer in answers.root} == {
        correct.answer_uid,
        wrong.answer_uid,
    }
