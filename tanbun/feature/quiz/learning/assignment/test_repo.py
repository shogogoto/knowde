"""クイズの学習者割り当てrepoのテスト."""

from neomodel import adb

from tanbun.conftest import async_fixture, mark_async_test
from tanbun.feature.domain.types import to_uuid
from tanbun.feature.quiz.candidate.types import CandidateType
from tanbun.feature.quiz.domain.parts import QuizType
from tanbun.feature.quiz.generation.repo import generate_quiz
from tanbun.feature.quiz.learning.assignment.repo import (
    assign_quiz_to_learner,
)
from tanbun.feature.quiz.learning.fixture import (
    fx_learning,
    learning_resource_id,
)
from tanbun.feature.quiz.learning.progress.repo import fetch_coverage
from tanbun.feature.tanbun.label import LSentence
from tanbun.feature.user.label import LUser
from tanbun.feature.user.testing import aregister

u = async_fixture()(fx_learning)


@mark_async_test()
async def test_assign_quiz_to_learner(u: LUser):
    """他人が作ったクイズを重複なく学習対象へ追加."""
    rid = await learning_resource_id(u.uid)
    target = LSentence.nodes.first(val="a")
    quiz = await generate_quiz(
        QuizType.TERM2SENT,
        CandidateType.ALL,
        target.uid,
        3,
        u.uid,
    )
    other = await aregister(email="learner@ex.com")

    creator_before = await fetch_coverage(rid, u.uid, QuizType.TERM2SENT)
    learner_before = await fetch_coverage(
        rid,
        other.uid,
        QuizType.TERM2SENT,
    )
    assert creator_before.covered == 1
    assert learner_before.covered == 0

    assert await assign_quiz_to_learner(quiz.quiz_id, other.uid)
    assert await assign_quiz_to_learner(quiz.quiz_id, other.uid)

    creator_after = await fetch_coverage(rid, u.uid, QuizType.TERM2SENT)
    learner_after = await fetch_coverage(
        rid,
        other.uid,
        QuizType.TERM2SENT,
    )
    assert creator_after == creator_before
    assert learner_after.covered == 1

    rows, _ = await adb.cypher_query(
        """
        MATCH (user: User {uid: $user_id})
            -[learn:LEARN]->(quiz: Quiz {uid: $quiz_id})
        RETURN COUNT(learn)
        """,
        params={
            "user_id": to_uuid(other.uid).hex,
            "quiz_id": to_uuid(quiz.quiz_id).hex,
        },
    )
    assert rows == [[1]]
