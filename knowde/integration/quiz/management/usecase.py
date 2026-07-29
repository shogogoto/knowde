"""Quiz管理usecase."""

from knowde.integration.quiz.management.errors import QuizNotFoundError
from knowde.integration.quiz.management.repo import delete_created_quiz
from knowde.shared.types import UUIDy


async def delete_quiz(
    quiz_id: UUIDy,
    user_id: UUIDy,
) -> None:
    """作成者本人のQuizを削除."""
    if not await delete_created_quiz(quiz_id, user_id):
        msg = f"削除できるQuizが見つかりません: {quiz_id}"
        raise QuizNotFoundError(msg=msg)
