"""Quiz管理のエラー."""

from fastapi import status

from knowde.feature.primitive.errors import DomainError


class QuizNotFoundError(DomainError):
    """所有するQuizが見つからなかった."""

    status_code = status.HTTP_404_NOT_FOUND
