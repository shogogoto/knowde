"""クイズ活動集計APIのテスト."""

from fastapi import status
from httpx import AsyncClient

from tanbun.conftest import mark_async_test
from tanbun.feature.user.testing import aauth_header, aregister


@mark_async_test()
async def test_get_monthly_quiz_achievement(ac: AsyncClient):
    """認証ユーザーは月間クイズ活動を取得できる."""
    user = await aregister("quiz-achievement-api@example.com")

    response = await ac.get(
        "/user/achievement/quiz/monthly",
        params={"year": 2026, "month": 8},
        headers=await aauth_header(user.email),
    )

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert len(result["days"]) == 31  # noqa: PLR2004
    assert result["total"]["n_work"] == 0


@mark_async_test()
async def test_get_monthly_quiz_achievement_requires_login(ac: AsyncClient):
    """他人の活動を無認証で取得できない."""
    response = await ac.get(
        "/user/achievement/quiz/monthly",
        params={"year": 2026, "month": 8},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
