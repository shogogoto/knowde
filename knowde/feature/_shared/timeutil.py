from datetime import datetime

from pytz import timezone

TZ = timezone("Asia/Tokyo")


def jst_now() -> datetime:
    """Jst datetime now."""
    return datetime.now(tz=TZ)
