"""Quiz管理usecaseのテスト."""

import pytest
from neomodel import adb

from tanbun.conftest import async_fixture, mark_async_test
from tanbun.feature.domain.types import to_uuid
from tanbun.feature.quiz.answering.repo import create_answer
from tanbun.feature.quiz.candidate.types import CandidateType
from tanbun.feature.quiz.domain.parts import QuizType
from tanbun.feature.quiz.fixture import fx_u
from tanbun.feature.quiz.generation.repo import generate_quiz
from tanbun.feature.quiz.management.errors import QuizNotFoundError
from tanbun.feature.quiz.management.usecase import delete_quiz
from tanbun.feature.tanbun.label import LSentence
from tanbun.feature.user.label import LUser
from tanbun.feature.user.testing import aregister

u = async_fixture()(fx_u)


@mark_async_test()
async def test_delete_quiz_and_answers_without_deleting_sentences(u: LUser):
    """QuizとAnswerだけを削除し、元のSentenceは残す."""
    target = LSentence.nodes.first(val="ccc")
    source = await generate_quiz(
        QuizType.TERM2SENT,
        CandidateType.ALL,
        target.uid,
        3,
        u.uid,
    )
    answer = await create_answer(
        source.quiz_id,
        source.to_readable().correct,
        u.uid,
    )

    await delete_quiz(source.quiz_id, u.uid)

    rows, _ = await adb.cypher_query(
        """
        RETURN
            EXISTS { MATCH (:Quiz {uid: $quiz_id}) },
            EXISTS { MATCH (:Answer {uid: $answer_id}) },
            EXISTS { MATCH (:Sentence {uid: $sentence_id}) }
        """,
        params={
            "quiz_id": source.quiz_id.hex,
            "answer_id": answer.answer_uid.hex,
            "sentence_id": to_uuid(target.uid).hex,
        },
    )
    assert rows == [[False, False, True]]


@mark_async_test()
async def test_reject_deleting_other_users_quiz(u: LUser):
    """作成者以外はQuizを削除できない."""
    other = await aregister(email="quiz-delete-other@ex.com")
    target = LSentence.nodes.first(val="ccc")
    source = await generate_quiz(
        QuizType.TERM2SENT,
        CandidateType.ALL,
        target.uid,
        3,
        other.uid,
    )

    with pytest.raises(QuizNotFoundError):
        await delete_quiz(source.quiz_id, u.uid)
