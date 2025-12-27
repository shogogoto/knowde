"""response object."""

from uuid import UUID

from pydantic import BaseModel

from knowde.integration.quiz.domain.domain import ReadableQuiz


class AnswerResult(BaseModel):
    """回答結果."""

    answer_uid: UUID
    is_correct: bool
    quiz: ReadableQuiz
