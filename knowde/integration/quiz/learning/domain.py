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


class QuizTargetSelector(StrEnum):
    """クイズ生成用のフィルタ."""

    UNCOVERED = auto()  # まだクイズなし
    LOW_ACCURACY = auto()  # 低正答率


class QuizTargetOrder(StrEnum):
    """クイズ生成用の単文の順番."""

    # ↓はクイズなしに算出できて別な気がする
    HIGH_SCORE = auto()
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
