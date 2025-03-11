"""時間util."""
from __future__ import annotations

from datetime import date, datetime

import pytz

TZ = pytz.timezone("Asia/Tokyo")  # pytz じゃないとneo4j driverには対応していないっぽい


def jst_now() -> datetime:  # noqa: D103
    return datetime.now(tz=TZ)


def to_date(s: str) -> date:  # noqa: D103
    dt = datetime.strptime(s, "%Y-%m-%d").astimezone(TZ)
    return dt.date()
