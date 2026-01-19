"""quiz router param."""

from pydantic import BaseModel

from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.sampling.types import SamplingType


class CreateQuizParam(BaseModel, frozen=True):
    """クイズ作成パラメータ."""

    target_sent_uid: str
    quiz_type: QuizType
    cand_type: CandidateType
    sampling_type: SamplingType
    n_option: int = 4
    allow_multiple_anwser: bool = False
    allow_no_correct_option: bool = False


class AnswerParam(BaseModel, frozen=True):
    """回答パラメータ."""

    selected: list[str]


class AnswerFeedback(BaseModel, frozen=True):
    """回答フィードバック."""

    is_correct: bool
