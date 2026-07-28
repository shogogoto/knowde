"""Quiz管理domain."""

from pydantic import BaseModel, Field

from knowde.feature.entry.mapper import MResource
from knowde.integration.quiz.domain.parts import QuizType
from knowde.shared.util import Neo4jDateTime


class QuizResourceStatus(BaseModel, frozen=True):
    """Resourceごとの作成済みQuiz状況."""

    resource: MResource
    total_quizzes: int
    quiz_counts: dict[QuizType, int] = Field(default_factory=dict)
    last_created_at: Neo4jDateTime
