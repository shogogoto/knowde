"""クイズ活動の成果API."""

from typing import Annotated

from fastapi import APIRouter, Query

from knowde.shared.user.router_util import ActiveUser

from .domain import MonthlyQuizAchievement
from .repo import fetch_monthly_quiz_achievement

router = APIRouter(prefix="/achievement/quiz", tags=["quiz_achievement"])


@router.get("/monthly")
async def get_monthly_quiz_achievement(
    user: ActiveUser,
    year: Annotated[int, Query(ge=2000, le=2100)],
    month: Annotated[int, Query(ge=1, le=12)],
) -> MonthlyQuizAchievement:
    """認証ユーザーの指定月のクイズ活動を取得."""
    return await fetch_monthly_quiz_achievement(user.uid, year, month)
