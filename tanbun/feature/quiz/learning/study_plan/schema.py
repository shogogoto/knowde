"""StudyPlan APIのschema."""

from uuid import UUID

from pydantic import BaseModel

from tanbun.feature.quiz.domain.domain import ReadableQuiz
from tanbun.feature.quiz.domain.parts import QuizType
from tanbun.feature.quiz.learning.recommendation.domain import (
    QuizRecommendation,
    QuizRecommendationReason,
)


class QuizRecommendationResponse(BaseModel, frozen=True):
    """resource情報を含む回答可能な推薦クイズ."""

    resource_id: UUID
    quiz_type: QuizType
    quiz: ReadableQuiz
    reason: QuizRecommendationReason

    @classmethod
    def from_domain(
        cls,
        recommendation: QuizRecommendation,
    ) -> "QuizRecommendationResponse":
        """domainモデルをAPIレスポンスへ変換."""
        return cls(
            resource_id=recommendation.resource_id,
            quiz_type=recommendation.quiz.quiz_type,
            quiz=recommendation.quiz.to_readable(),
            reason=recommendation.reason,
        )
