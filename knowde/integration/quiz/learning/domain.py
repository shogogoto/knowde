"""学習度管理."""

from enum import StrEnum, auto

from pydantic import BaseModel

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


class Ratio(BaseModel, frozen=True):
    """全体とtargetの比率でaccuracyやcovorageを表現する."""

    total: int
    n_target: int  # covered or correct ...

    def __call__(self) -> float:  # noqa: D102
        if self.total == 0:
            return 0.0
        return self.n_target / self.total


# ResourceStats と クイズ統計の組み合わせ
# クイズ統計取得がまだできていない
class ResourceCoverage(BaseModel, frozen=True):
    """クイズ化された率.

    n_rel_quiz / n_rel
    n_term_quiz / n_term
    n_quiz / n_sent
    """
