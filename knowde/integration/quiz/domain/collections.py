"""domainのコレクション."""

from pydantic import BaseModel, RootModel

from knowde.integration.quiz.domain.domain import ReadableQuiz


class ReadableQuizzes(RootModel[list[ReadableQuiz]]):
    """ReadableQuizのコレクション."""


class ReadableQuizResult(BaseModel, frozen=True):
    """totalをつけるためのもの."""

    data: ReadableQuizzes
    total: int
