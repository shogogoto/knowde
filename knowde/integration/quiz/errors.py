"""quiz errors."""

from knowde.shared.errors import DomainError


class QuizOptionsMustBeDefError(DomainError):
    """クイズ対象はDefでなければならない."""


class AnswerError(DomainError):
    """回答エラー."""
