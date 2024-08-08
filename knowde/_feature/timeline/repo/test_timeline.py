"""子をすべて削除."""
from pytest_unordered import unordered

from knowde._feature.timeline.domain.domain import TimeValue
from knowde._feature.timeline.repo.fetch import fetch_time
from knowde._feature.timeline.repo.timeline import list_time


def test_timeline_days() -> None:
    """日timesを取得."""
    rng = range(1, 4)
    for i in rng:
        fetch_time("x", 2024, 12, i)
    assert list_time("y") == []  # when empty
    assert list_time("x") == unordered(
        [TimeValue(name="x", year=2024, month=12, day=i) for i in rng],
    )


def test_timeline_months() -> None:
    """月timesを取得."""
    rng = range(1, 4)
    for i in rng:
        fetch_time("x", 2024, i)
    assert list_time("x") == unordered(
        [TimeValue(name="x", year=2024, month=i) for i in rng],
    )


def test_timeline_years() -> None:
    """年timesを取得."""
    rng = range(2020, 2024)
    for i in rng:
        fetch_time("x", i)
    assert list_time("x") == unordered(
        [TimeValue(name="x", year=i) for i in rng],
    )
