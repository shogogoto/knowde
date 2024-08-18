"""test."""
from knowde.primitive.time.repo.fetch import fetch_time
from knowde.primitive.time.repo.query import find_times_from


def test_find_from_day() -> None:  # noqa: D103
    t = fetch_time("x", 1, 1, 1)
    assert find_times_from("x", t.day.valid_uid) == [t]


def test_find_from_month() -> None:  # noqa: D103
    t = fetch_time("x", 2, 2)
    assert find_times_from("x", t.month.valid_uid) == [t]


def test_find_from_year() -> None:  # noqa: D103
    t = fetch_time("x", 3)
    assert find_times_from("x", t.year.valid_uid) == [t]
