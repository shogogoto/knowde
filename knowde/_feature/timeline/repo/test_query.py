from knowde._feature.timeline.repo.fetch import fetch_time
from knowde._feature.timeline.repo.query import find_times_from


def test_find_from_day() -> None:
    t = fetch_time("x", 1, 1, 1)
    assert find_times_from("x", t.day.valid_uid) == [t]


def test_find_from_month() -> None:
    t = fetch_time("x", 2, 2)
    assert find_times_from("x", t.month.valid_uid) == [t]


def test_find_from_year() -> None:
    t = fetch_time("x", 3)
    assert find_times_from("x", t.year.valid_uid) == [t]
