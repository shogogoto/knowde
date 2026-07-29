"""複数リソースを横断するクイズ推薦."""

from enum import StrEnum, auto
from uuid import UUID

from pydantic import BaseModel

from knowde.integration.quiz.domain.domain import QuizSource


class QuizRecommendationReason(StrEnum):
    """このクイズを推薦した理由."""

    UNATTEMPTED = auto()
    LOW_ACCURACY = auto()
    COVERAGE = auto()


class QuizRecommendation(BaseModel, frozen=True):
    """どのリソースについて解くクイズかを含む推薦."""

    resource_id: UUID
    quiz: QuizSource
    reason: QuizRecommendationReason
