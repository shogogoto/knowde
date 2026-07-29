"""Quiz管理domain."""

from uuid import UUID

from pydantic import BaseModel, Field

from knowde.feature.entry.mapper import MResource
from knowde.integration.quiz.domain.domain import ReadableQuiz
from knowde.integration.quiz.domain.parts import QuizType
from knowde.shared.util import Neo4jDateTime


class QuizResourceStatus(BaseModel, frozen=True):
    """Resourceごとの作成済みQuiz状況."""

    resource: MResource
    total_quizzes: int
    quiz_counts: dict[QuizType, int] = Field(default_factory=dict)
    last_created_at: Neo4jDateTime


class SentenceQuizStatus(BaseModel, frozen=True):
    """単文を対象として作成したQuiz状況."""

    sentence_id: UUID
    total_quizzes: int
    quiz_counts: dict[QuizType, int] = Field(default_factory=dict)


class ManagedQuiz(BaseModel, frozen=True):
    """回答状況を含む管理対象Quiz."""

    quiz: ReadableQuiz
    attempts: int
    corrects: int
    accuracy: float | None
    last_attempted_at: Neo4jDateTime | None


class ManagedQuizResult(BaseModel, frozen=True):
    """管理対象Quizのページング結果."""

    data: list[ManagedQuiz]
    total: int
