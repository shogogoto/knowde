from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

TZ = timezone(timedelta(hours=9), "Asia/Tokyo")


def jst_now() -> datetime:
    return datetime.now(tz=TZ)


def to_date(s: str) -> date:
    dt = datetime.strptime(s, "%Y-%m-%d").astimezone(TZ)
    return dt.date()
