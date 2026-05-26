"""quiz router param."""

from pydantic import BaseModel

from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.parts import QuizType


class BatchCreateQuizParam(BaseModel, frozen=True):
    """リソース単位で一括クイズ作成."""

    resource_uid: str
    n_quiz: int
    quiz_type: QuizType
    cand_type: CandidateType
    n_option: int = 4
    allow_multiple_anwser: bool = False
    allow_no_correct_option: bool = False


class CreateQuizParam(BaseModel, frozen=True):
    """指定単文からクイズ作成."""

    target_sent_uid: str
    quiz_type: QuizType
    cand_type: CandidateType
    n_option: int = 4
    allow_multiple_anwser: bool = False
    allow_no_correct_option: bool = False
    user_uid: str


# create_quizの引数そのまま
# 欲しくなったら実装
# class CreateQuizManuallyParam(BaseModel, frozen=True):
#     """選択肢などすべてユーザーが選ぶ."""


class AnswerParam(BaseModel, frozen=True):
    """回答パラメータ."""

    selected: list[str]


class AnswerFeedback(BaseModel, frozen=True):
    """回答フィードバック."""

    is_correct: bool
