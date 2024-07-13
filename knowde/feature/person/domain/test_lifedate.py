"""人生日付 test."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from .lifedate import LifeDate, LifeDateInvalidError


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
    """Valid lifedate."""
    assert LifeDate(year=year, month=month, day=day).to_str() == expected


def test_lifedate_invalid() -> None:
    """Invalid lifedate."""
    with pytest.raises(LifeDateInvalidError):
        LifeDate(year=2024, month=None, day=28)


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
    """Invalid lifedate."""
    with pytest.raises(ValidationError):
        LifeDate(year=year, month=month, day=day)


@pytest.mark.parametrize(
    ("year", "month", "day", "s"),
    [
        (2024, 3, 28, "20240328"),
        (2024, 3, None, "20240399"),
        (2024, None, None, "20249999"),
        (-500, None, None, "-5009999"),
    ],
)
def test_from_str(
    year: int,
    month: int | None,
    day: int | None,
    s: str,
) -> None:
    """From str instantiate."""
    assert LifeDate.from_str(s) == LifeDate(year=year, month=month, day=day)
