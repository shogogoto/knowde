"""クイズ活動の集計repo."""

from calendar import monthrange
from datetime import date, datetime

from neomodel import adb

from knowde.feature.domain.datetime import TZ, neo4j_dt_validator
from knowde.feature.domain.types import UUIDy, to_uuid

from .domain import (
    DailyQuizAchievement,
    MonthlyQuizAchievement,
    QuizAchievementCounts,
)


def _month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
    # pytzではtzinfo=TZではなくlocalizeを使わないと不正な歴史的offsetになる。
    start = TZ.localize(datetime(year, month, 1))  # noqa: DTZ001
    if month == 12:  # noqa: PLR2004
        return start, TZ.localize(datetime(year + 1, 1, 1))  # noqa: DTZ001
    return start, TZ.localize(datetime(year, month + 1, 1))  # noqa: DTZ001


async def fetch_monthly_quiz_achievement(
    user_id: UUIDy,
    year: int,
    month: int,
) -> MonthlyQuizAchievement:
    """ユーザーのクイズ作成・回答を指定月の日別に集計."""
    start, end = _month_bounds(year, month)
    rows, _ = await adb.cypher_query(
        """
        MATCH (user:User {uid: $user_id})
        CALL (user) {
            MATCH (user)-[:CREATE]->(quiz:Quiz)
            WHERE quiz.created >= datetime($start)
                AND quiz.created < datetime($end)
            RETURN quiz.created AS created,
                "created" AS activity,
                false AS is_correct
            UNION ALL
            MATCH (user)-[:ANSWER]->(answer:Answer)
            WHERE answer.created >= datetime($start)
                AND answer.created < datetime($end)
            RETURN answer.created AS created,
                "answered" AS activity,
                answer.is_correct AS is_correct
        }
        RETURN created, activity, is_correct
        ORDER BY created
        """,
        params={
            "user_id": to_uuid(user_id).hex,
            "start": start.isoformat(),
            "end": end.isoformat(),
        },
    )

    counts = {
        day: {"created": 0, "answered": 0, "correct": 0}
        for day in range(1, monthrange(year, month)[1] + 1)
    }
    for created, activity, is_correct in rows:
        occurred_at = neo4j_dt_validator(created).astimezone(TZ)
        day_counts = counts[occurred_at.day]
        if activity == "created":
            day_counts["created"] += 1
        else:
            day_counts["answered"] += 1
            day_counts["correct"] += int(is_correct)

    days = [
        DailyQuizAchievement(
            date=date(year, month, day),
            n_quiz_created=value["created"],
            n_quiz_answered=value["answered"],
            n_quiz_correct=value["correct"],
        )
        for day, value in counts.items()
    ]
    total = QuizAchievementCounts(
        n_quiz_created=sum(day.n_quiz_created for day in days),
        n_quiz_answered=sum(day.n_quiz_answered for day in days),
        n_quiz_correct=sum(day.n_quiz_correct for day in days),
    )
    return MonthlyQuizAchievement(year=year, month=month, days=days, total=total)
