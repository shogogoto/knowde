"""QuizChainのdomain."""

from enum import StrEnum, auto
from uuid import UUID

from pydantic import BaseModel

from knowde.integration.quiz.domain.domain import ReadableQuiz
from knowde.integration.quiz.domain.parts import QuizType


class QuizChainRole(StrEnum):
    """Quizから見たSentenceの役割."""

    TARGET = auto()
    OPTION = auto()
    CORRECT = auto()


class QuizChainSentence(BaseModel, frozen=True):
    """QuizChain上のSentence."""

    sentence_id: UUID
    sentence: str
    resource_id: UUID


class QuizChainQuiz(BaseModel, frozen=True):
    """QuizChain上のQuiz."""

    quiz_id: UUID
    quiz_type: QuizType
    readable: ReadableQuiz


class QuizChainLink(BaseModel, frozen=True):
    """QuizとSentenceを結ぶ役割付きlink."""

    quiz_id: UUID
    sentence_id: UUID
    role: QuizChainRole


class QuizChain(BaseModel, frozen=True):
    """frontendで既存chainへマージできる1ホップ分のgraph."""

    sentences: list[QuizChainSentence]
    quizzes: list[QuizChainQuiz]
    links: list[QuizChainLink]
