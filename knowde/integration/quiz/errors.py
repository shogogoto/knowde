"""quiz errors."""

from knowde.shared.errors import DomainError


class QuizOptionsMustBeDefError(DomainError):
    """クイズ対象はDefでなければならない."""


class AnswerError(DomainError):
    """回答エラー."""


class QuizDuplicateError(DomainError):
    """同一クイズ重複エラー."""
