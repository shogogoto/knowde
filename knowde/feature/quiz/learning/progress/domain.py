"""クイズ学習の進捗."""

from uuid import UUID

from pydantic import BaseModel, computed_field

from knowde.feature.domain.datetime import Neo4jDateTime
from knowde.feature.quiz.domain.parts import QuizType


class QuizCoverage(BaseModel, frozen=True):
    """リソース毎タイプ毎のクイズ化された単文率."""

    resource_id: UUID
    user_id: UUID
    quiz_type: QuizType
    eligible: int
    covered: int

    @computed_field
    @property
    def ratio(self) -> float:  # noqa: D102
        if self.eligible == 0:
            return 0.0
        return self.covered / self.eligible


class QuizAttemptRate(BaseModel, frozen=True):
    """用意されたクイズのうち回答した取り組み割合."""

    resource_id: UUID
    user_id: UUID
    quiz_type: QuizType
    available: int
    attempted: int

    @computed_field
    @property
    def ratio(self) -> float:  # noqa: D102
        if self.available == 0:
            return 0.0
        return self.attempted / self.available


class QuizPerformance(BaseModel, frozen=True):
    """クイズ回答の成績."""

    resource_id: UUID
    user_id: UUID
    quiz_type: QuizType
    attempts: int
    corrects: int
    last_attempted_at: Neo4jDateTime | None

    @computed_field
    @property
    def accuracy(self) -> float:  # noqa: D102
        if self.attempts == 0:
            return 0.0
        return self.corrects / self.attempts


class QuizTypeLearningStatus(BaseModel, frozen=True):
    """QuizTypeごとの学習状況."""

    coverage: QuizCoverage
    attempt_rate: QuizAttemptRate
    performance: QuizPerformance


class ResourceLearningStatus(BaseModel, frozen=True):
    """リソースについてQuizTypeを横断した学習状況."""

    resource_id: UUID
    user_id: UUID
    by_quiz_type: dict[QuizType, QuizTypeLearningStatus]

    @computed_field
    @property
    def overall_coverage(self) -> float:
        """全QuizTypeの適格単文に対するクイズ化率."""
        eligible = sum(s.coverage.eligible for s in self.by_quiz_type.values())
        if eligible == 0:
            return 0.0
        covered = sum(s.coverage.covered for s in self.by_quiz_type.values())
        return covered / eligible

    @computed_field
    @property
    def overall_attempt_rate(self) -> float:
        """全QuizTypeのクイズに対する取り組み率."""
        available = sum(s.attempt_rate.available for s in self.by_quiz_type.values())
        if available == 0:
            return 0.0
        attempted = sum(s.attempt_rate.attempted for s in self.by_quiz_type.values())
        return attempted / available

    @computed_field
    @property
    def overall_accuracy(self) -> float:
        """全QuizTypeの回答に対する正答率."""
        attempts = sum(s.performance.attempts for s in self.by_quiz_type.values())
        if attempts == 0:
            return 0.0
        corrects = sum(s.performance.corrects for s in self.by_quiz_type.values())
        return corrects / attempts

    @computed_field
    @property
    def last_attempted_at(self) -> Neo4jDateTime | None:
        """全QuizTypeで最後に回答した日時."""
        attempted_at = [
            s.performance.last_attempted_at
            for s in self.by_quiz_type.values()
            if s.performance.last_attempted_at is not None
        ]
        return max(attempted_at, default=None)
