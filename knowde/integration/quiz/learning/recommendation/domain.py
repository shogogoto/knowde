"""複数リソースを横断するクイズ推薦."""

from uuid import UUID

from pydantic import BaseModel

from knowde.integration.quiz.domain.domain import QuizSource


class QuizRecommendation(BaseModel, frozen=True):
    """どのリソースについて解くクイズかを含む推薦."""

    resource_id: UUID
    quiz: QuizSource
