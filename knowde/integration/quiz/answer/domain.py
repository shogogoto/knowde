"""回答ドメイン."""

from uuid import UUID

from pydantic import BaseModel

from knowde.integration.quiz.domain.domain import ReadableQuiz
from knowde.shared.user.schema import UserReadPublic


class Answer(BaseModel, frozen=True):
    """誰がいつ何を選択して回答したか、とその正誤."""

    answer_uid: UUID
    selected: list[str]  # 複数選択可
    is_correct: bool
    quiz: ReadableQuiz
    who: UserReadPublic
