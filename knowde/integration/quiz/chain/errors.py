"""QuizChainのエラー."""

from fastapi import status

from knowde.shared.errors import DomainError


class QuizChainNotFoundError(DomainError):
    """閲覧可能なQuizChainの起点が見つからない."""

    status_code = status.HTTP_404_NOT_FOUND
