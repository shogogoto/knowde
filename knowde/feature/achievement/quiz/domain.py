"""クイズ活動の成果モデル."""

from datetime import date

from pydantic import BaseModel, computed_field


class QuizAchievementCounts(BaseModel, frozen=True):
    """クイズに関する作業数."""

    n_quiz_created: int = 0
    n_quiz_answered: int = 0
    n_quiz_correct: int = 0

    @computed_field
    @property
    def n_work(self) -> int:
        """作成と回答をそれぞれ一作業として数える."""
        return self.n_quiz_created + self.n_quiz_answered


class DailyQuizAchievement(QuizAchievementCounts, frozen=True):
    """一日分のクイズ活動."""

    date: date


class MonthlyQuizAchievement(BaseModel, frozen=True):
    """指定月の日別クイズ活動と月間合計."""

    year: int
    month: int
    days: list[DailyQuizAchievement]
    total: QuizAchievementCounts
