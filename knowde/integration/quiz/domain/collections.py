"""domainのコレクション."""

from pydantic import BaseModel, RootModel

from knowde.integration.quiz.domain.domain import ReadableQuiz


class ReadableQuizCollection(RootModel[list[ReadableQuiz]]):
    """ReadableQuizのコレクション."""


class ReadableQuizResult(BaseModel, frozen=True):
    """totalをつけるためのもの."""

    data: ReadableQuizCollection
    total: int
