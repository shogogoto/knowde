"""Quiz管理usecase."""

from tanbun.feature.domain.types import UUIDy
from tanbun.feature.quiz.management.errors import QuizNotFoundError
from tanbun.feature.quiz.management.repo import delete_created_quiz


async def delete_quiz(
    quiz_id: UUIDy,
    user_id: UUIDy,
) -> None:
    """作成者本人のQuizを削除."""
    if not await delete_created_quiz(quiz_id, user_id):
        msg = f"削除できるQuizが見つかりません: {quiz_id}"
        raise QuizNotFoundError(msg=msg)
