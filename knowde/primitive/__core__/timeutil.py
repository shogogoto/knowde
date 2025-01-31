"""時間util."""
from __future__ import annotations

from datetime import date, datetime

from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Tokyo")


def jst_now() -> datetime:  # noqa: D103
    return datetime.now(tz=TZ)


def to_date(s: str) -> date:  # noqa: D103
    dt = datetime.strptime(s, "%Y-%m-%d").astimezone(TZ)
    return dt.date()
