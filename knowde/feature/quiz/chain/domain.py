"""QuizChainのdomain."""

from enum import StrEnum, auto
from uuid import UUID

from pydantic import BaseModel, Field

from knowde.feature.quiz.domain.answer import Answer
from knowde.feature.quiz.domain.domain import ReadableQuiz
from knowde.feature.quiz.domain.parts import QuizType
from knowde.feature.quiz.domain.rel import QuizRel
from knowde.feature.tanbun.domain import Tanbun


class QuizChainRole(StrEnum):
    """Quizから見たSentenceの役割."""

    TARGET = auto()
    OPTION = auto()
    CORRECT = auto()


class QuizChainQuiz(BaseModel, frozen=True):
    """QuizChain上のQuiz."""

    quiz_id: UUID
    quiz_type: QuizType
    readable: ReadableQuiz


class QuizChainLink(BaseModel, frozen=True):
    """QuizとTanbunを結ぶ役割と、targetからの知識関係."""

    quiz_id: UUID
    sentence_id: UUID
    role: QuizChainRole
    relations: list[QuizRel] = Field(default_factory=list)


class QuizChain(BaseModel, frozen=True):
    """frontendで既存chainへマージできる1ホップ分のgraph."""

    sentences: list[Tanbun]
    quizzes: list[QuizChainQuiz]
    links: list[QuizChainLink]
    answers: list[Answer] = Field(default_factory=list)
