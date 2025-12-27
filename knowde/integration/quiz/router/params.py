"""quiz router param."""

from pydantic import BaseModel

from knowde.integration.quiz.domain.parts import QuizType


class CreateQuizParam(BaseModel, frozen=True):
    """クイズ作成パラメータ."""

    target_sent_uid: str
    quiz_type: QuizType
    radius: int
    n_option: int


class AnswerParam(BaseModel, frozen=True):
    """回答パラメータ."""

    selected: list[str]


class AnswerFeedback(BaseModel, frozen=True):
    """回答フィードバック."""

    is_correct: bool
