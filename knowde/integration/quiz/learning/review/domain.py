"""復習用に準備したクイズ."""

from enum import StrEnum, auto

from pydantic import BaseModel

from knowde.integration.quiz.domain.domain import QuizSource


class ReviewQuizKind(StrEnum):
    """復習クイズを選んだ根拠."""

    UNATTEMPTED = auto()
    LOW_ACCURACY = auto()


class PreparedReviewQuiz(BaseModel, frozen=True):
    """根拠を保持した復習クイズ."""

    quiz: QuizSource
    kind: ReviewQuizKind
