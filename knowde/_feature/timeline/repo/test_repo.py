import pytest

from knowde._feature.timeline.domain.errors import DayRangeError, MonthRangeError
from knowde._feature.timeline.repo.repo import (
    fetch_day,
    fetch_month,
    fetch_timeline,
    fetch_year,
)


def test_fetch_timeline() -> None:
    tl1 = fetch_timeline("xxx").to_model()
    assert tl1 == fetch_timeline("xxx").to_model()
    assert tl1 != fetch_timeline("yyy").to_model()


def test_fetch_year() -> None:
    y1 = fetch_year("xxx", 2024)
    assert y1 == fetch_year("xxx", 2024)
    assert y1 != fetch_year("xxx", 2025)
    assert y1 != fetch_year("yyy", 2024)


def test_fetch_month() -> None:
    ym1 = fetch_month("xxx", 2024, 1)
    assert ym1 == fetch_month("xxx", 2024, 1)
    assert ym1 != fetch_month("xxx", 2025, 1)
    assert ym1 != fetch_month("yyy", 2025, 1)
    assert ym1 != fetch_month("xxx", 2024, 12)
    with pytest.raises(MonthRangeError):
        fetch_month("xxx", 2025, 0)
    with pytest.raises(MonthRangeError):
        fetch_month("xxx", 2025, 13)


def test_fetch_day() -> None:
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


# def test_add_yyyymmdd() -> None:
#     ad = add_timeline("A.D.")  # Anno Domini 主の年に
#     t = add_time("A.D.", 1999, 1, 1)
