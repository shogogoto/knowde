"""Quiz管理usecaseのテスト."""

import pytest
from neomodel import adb

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.answering.repo import create_answer
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.generation.repo import generate_quiz
from knowde.integration.quiz.management.errors import QuizNotFoundError
from knowde.integration.quiz.management.usecase import delete_quiz
from knowde.shared.knowde.label import LSentence
from knowde.shared.types import to_uuid
from knowde.shared.user.label import LUser
from knowde.shared.user.testing import aregister

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
