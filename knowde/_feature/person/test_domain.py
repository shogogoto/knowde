from __future__ import annotations

import pytest
from pydantic import ValidationError

from .domain import LifeDate
from .errors import UnclearLifeDateError


@pytest.mark.parametrize(
    ("year", "month", "day", "expected"),
    [
        (2024, 3, 28, "20240328"),
        (2024, 3, None, "20240399"),
        (2024, None, None, "20249999"),
        (-500, None, None, "-5009999"),
    ],
)
def test_lifedate_valid(
    year: int,
    month: int | None,
    day: int | None,
    expected: str,
) -> None:
    assert LifeDate(year=year, month=month, day=day).to_str() == expected


@pytest.mark.parametrize(
    ("year", "month", "day"),
    [
        (2024, None, 28),
    ],
)
def test_lifedate_invalid(year: int, month: int | None, day: int | None) -> None:
    with pytest.raises(UnclearLifeDateError):
        LifeDate(year=year, month=month, day=day)


@pytest.mark.parametrize(
    ("year", "month", "day"),
    [
        (2024, -1, 28),
        (2024, 0, 28),
        (2024, 13, 280),
        (2024, 3, -0),
        (2024, 3, 0),
        (2024, 3, 32),
    ],
)
def test_lifedate_invalid_value(year: int, month: int | None, day: int | None) -> None:
    with pytest.raises(ValidationError):
        LifeDate(year=year, month=month, day=day)
