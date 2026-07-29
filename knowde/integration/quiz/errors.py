"""quiz errors."""

from knowde.shared.errors import DomainError


class QuizOptionsMustBeDefError(DomainError):
    """クイズ対象はDefでなければならない."""


class SamplingError(DomainError):
    """選択肢サンプル数が不正."""


class InsufficientOptionsError(DomainError):
    """クイズの選択肢不足."""


class InvalidAnswerOptionError(DomainError):
    """回答選択肢が範囲外."""


class QuizDuplicateError(DomainError):
    """同一クイズ重複エラー."""


class QuizRestoreError(DomainError):
    """保存済みクイズを回答可能な形へ復元できない."""


class AnswerFailedError(DomainError):
    """回答失敗(到達しないはずのコード)."""
