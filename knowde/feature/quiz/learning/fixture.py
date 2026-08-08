"""テスト用データ."""

from uuid import UUID

from knowde.feature.domain.types import UUIDy, to_uuid
from knowde.feature.entry.namespace import fetch_namespace
from knowde.feature.entry.resource.usecase import save_text
from knowde.feature.quiz.answering.repo import create_answer
from knowde.feature.quiz.candidate.types import CandidateType
from knowde.feature.quiz.domain.answer import Answer
from knowde.feature.quiz.domain.domain import QuizSource
from knowde.feature.quiz.domain.parts import QuizType
from knowde.feature.quiz.learning.fill.usecase import generate_quizzes
from knowde.feature.quiz.learning.selection.domain import QuizFillStrategy
from knowde.feature.user.label import LUser
from knowde.feature.user.testing import aregister


async def fx_learning() -> LUser:  # noqa: D103
    u = await aregister(email="quiz@ex.com")
    u.username = "quiz"
    await u.save()
    s = """
        # title
            A: a
            B: b
            C: c
            D: d
            S: s
                s1
                s2
                <- pre_s
    """
    _sn, _m = await save_text(u.uid, s)
    return u


async def learning_resource_id(user_id: UUIDy) -> UUIDy:
    """学習テスト用ユーザーが持つリソースID."""
    namespace = await fetch_namespace(user_id)
    return namespace.resources[0].uid


async def create_learning_test_resource(user_id: UUIDy) -> UUID:
    """複数resourceを扱う学習テスト用のresourceを作成."""
    _, resource = await save_text(
        user_id,
        """
        # second
            X: x
            Y: y
            Z: z
        """,
    )
    return to_uuid(resource.uid)


async def generate_test_quizzes(
    resource_id: UUIDy,
    user_id: UUIDy,
    n_quiz: int,
    *,
    quiz_type: QuizType = QuizType.TERM2SENT,
    strategy: QuizFillStrategy = QuizFillStrategy.IMPORTANCE,
) -> list[QuizSource]:
    """学習テストの標準設定でクイズを生成."""
    return await generate_quizzes(
        resource_id,
        user_id,
        quiz_type,
        strategy,
        CandidateType.ALL,
        n_quiz=n_quiz,
        n_option=3,
    )


async def answer_test_quiz(
    quiz: QuizSource,
    user_id: UUIDy,
    *,
    correctly: bool,
) -> Answer:
    """学習テスト用クイズへ正解または不正解で回答."""
    readable = quiz.to_readable()
    selected = readable.correct if correctly else [readable.distractors[0]]
    return await create_answer(readable.quiz_id, selected, user_id)
