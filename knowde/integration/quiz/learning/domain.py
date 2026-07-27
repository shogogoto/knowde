"""学習度管理."""

from enum import StrEnum, auto
from uuid import UUID

from pydantic import BaseModel, computed_field

from knowde.integration.quiz.domain.parts import QuizType

# covorage
# accuracy 正答率


class QuizFillStrategy(StrEnum):
    """クイズ生成方式."""

    COVERAGE = auto()  # クイズなし単文
    REVIEW = auto()  # 低accuracy単文
    IMPORTANCE = auto()  # 高スコアでクイズなし単文
    # スコアとaccuracy の組み合わせのような指標が要るかも
    RANDOM = auto()  # ランダム


class QuizTargetPool(StrEnum):
    """クイズ対象を選ぶ母集団."""

    UNCOVERED = auto()  # まだクイズなし
    COVERED = auto()  # クイズあり


class QuizTargetOrder(StrEnum):
    """クイズ生成用の単文の順番."""

    HIGH_SCORE = auto()
    LOW_SCORE = auto()
    RANDOM = auto()


class QuizCoverage(BaseModel, frozen=True):
    """リソース毎タイプ毎のクイズ化された単文率."""

    resource_id: UUID
    user_id: UUID
    quiz_type: QuizType
    eligible: int  # 適格
    covered: int

    @computed_field
    @property
    def ratio(self) -> float:  # noqa: D102
        if self.eligible == 0:
            return 0.0
        return self.covered / self.eligible


# class ResourceLearningStats(BaseModel):
#     resource_id: UUID
#     user_id: UUID
#     quiz_type: QuizType
#     coverage: Ratio
#     attempt_rate: Ratio
#     accuracy: Ratio
#     last_attempted_at: datetime | None

#
# coverage
#   クイズを用意できているか
#
# attempt rate
#   用意されたクイズに回答したか
#
# accuracy
#   回答結果が正しかったか
#
# recency
#   最近復習したか
