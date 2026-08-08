"""クイズ活動集計のテスト."""

from neomodel import adb

from knowde.conftest import mark_async_test
from knowde.feature.user.testing import aregister

from .repo import fetch_monthly_quiz_achievement


async def _create_activity(user_id: str) -> None:
    await adb.cypher_query(
        """
        MATCH (user:User {uid: $user_id})
        CREATE
            (august1:Quiz {
                uid: "august-1",
                created: datetime("2026-08-01T00:10:00+09:00")
            }),
            (august15:Quiz {
                uid: "august-15",
                created: datetime("2026-08-15T12:00:00+09:00")
            }),
            (july:Quiz {
                uid: "july",
                created: datetime("2026-07-31T23:59:59+09:00")
            }),
            (september:Quiz {
                uid: "september",
                created: datetime("2026-09-01T00:00:00+09:00")
            }),
            (correct:Answer {
                uid: "correct",
                created: datetime("2026-08-01T09:00:00+09:00"),
                is_correct: true
            }),
            (incorrect:Answer {
                uid: "incorrect",
                created: datetime("2026-08-01T10:00:00+09:00"),
                is_correct: false
            }),
            (user)-[:CREATE]->(august1),
            (user)-[:CREATE]->(august15),
            (user)-[:CREATE]->(july),
            (user)-[:CREATE]->(september),
            (user)-[:ANSWER]->(correct),
            (user)-[:ANSWER]->(incorrect)
        """,
        params={"user_id": user_id},
    )


@mark_async_test()
async def test_fetch_monthly_quiz_achievement():
    """指定月の日別作業数と月間合計を返す."""
    user = await aregister("quiz-achievement@example.com")
    await _create_activity(user.uid)

    result = await fetch_monthly_quiz_achievement(user.uid, 2026, 8)

    assert len(result.days) == 31  # noqa: PLR2004
    assert result.days[0].model_dump() == {
        "date": result.days[0].date,
        "n_quiz_created": 1,
        "n_quiz_answered": 2,
        "n_quiz_correct": 1,
        "n_work": 3,
    }
    assert result.days[14].n_quiz_created == 1
    assert result.days[1].n_work == 0
    assert result.total.model_dump() == {
        "n_quiz_created": 2,
        "n_quiz_answered": 2,
        "n_quiz_correct": 1,
        "n_work": 4,
    }


@mark_async_test()
async def test_fetch_monthly_quiz_achievement_without_activity():
    """活動がない月にもゼロ件の日を返す."""
    user = await aregister("no-quiz-achievement@example.com")

    result = await fetch_monthly_quiz_achievement(user.uid, 2024, 2)

    assert len(result.days) == 29  # noqa: PLR2004
    assert all(day.n_work == 0 for day in result.days)
    assert result.total.n_work == 0
