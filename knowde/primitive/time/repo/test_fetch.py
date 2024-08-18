"""test."""
import pytest

from knowde.primitive.time.domain.errors import DayRangeError, MonthRangeError
from knowde.primitive.time.repo.fetch import (
    fetch_day,
    fetch_month,
    fetch_time,
    fetch_timeline,
    fetch_year,
)


def test_fetch_timeline() -> None:  # noqa: D103
    tl1 = fetch_timeline("xxx")
    assert tl1 == fetch_timeline("xxx")
    assert tl1 != fetch_timeline("yyy")


def test_fetch_year() -> None:  # noqa: D103
    y1 = fetch_year("xxx", 2024)
    assert y1 == fetch_year("xxx", 2024)
    assert y1 != fetch_year("xxx", 2025)
    assert y1 != fetch_year("yyy", 2024)


def test_fetch_month() -> None:  # noqa: D103
    ym1 = fetch_month("xxx", 2024, 1)
    assert ym1 == fetch_month("xxx", 2024, 1)
    assert ym1 != fetch_month("xxx", 2025, 1)
    assert ym1 != fetch_month("yyy", 2025, 1)
    assert ym1 != fetch_month("xxx", 2024, 12)
    with pytest.raises(MonthRangeError):
        fetch_month("xxx", 2025, 0)
    with pytest.raises(MonthRangeError):
        fetch_month("xxx", 2025, 13)


def test_fetch_day() -> None:  # noqa: D103
    ymd = fetch_day("xxx", 2024, 1, 1)
    assert ymd == fetch_day("xxx", 2024, 1, 1)
    assert ymd != fetch_day("zzz", 2024, 1, 1)
    assert ymd != fetch_day("xxx", 2025, 1, 1)
    assert ymd != fetch_day("xxx", 2024, 6, 1)
    assert ymd != fetch_day("xxx", 2024, 1, 31)
    with pytest.raises(DayRangeError):
        fetch_day("xxx", 2024, 1, 0)
    with pytest.raises(DayRangeError):
        fetch_day("xxx", 2024, 1, 32)


def test_fetch_time() -> None:
    """Facade."""
    n = "A.D."
    assert fetch_time(n, 2000) == fetch_year(n, 2000)  # Anno Domini 主の年に
    assert fetch_time(n, 2001, 1) == fetch_month(n, 2001, 1)
    assert fetch_time(n, 2002, 2, 1) == fetch_day(n, 2002, 2, 1)
