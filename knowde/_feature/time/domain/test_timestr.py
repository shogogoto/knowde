from __future__ import annotations

import pytest

from .const import SOCIETY_TIMELINE
from .domain import TimeValue
from .timestr import TimeStr


@pytest.mark.parametrize(
    ("string", "year", "month", "day", "tl"),
    [
        ("2000/01/01", 2000, 1, 1, SOCIETY_TIMELINE),
        ("2000/01", 2000, 1, None, SOCIETY_TIMELINE),
        ("2000", 2000, None, None, SOCIETY_TIMELINE),
        ("-2000", -2000, None, None, SOCIETY_TIMELINE),
        ("-20@XXX", -20, None, None, "XXX"),
        ("-20/12@XXX", -20, 12, None, "XXX"),
        ("-20/12/31@@XX", -20, 12, 31, "@XX"),
        ("@XXX", None, None, None, "XXX"),
        ("@", None, None, None, SOCIETY_TIMELINE),
    ],
)
def test_timestr(
    string: str,
    year: int,
    month: int | None,
    day: int | None,
    tl: str,
) -> None:
    v = TimeValue.new(tl, year, month, day)
    assert TimeStr(value=string).val == v
    assert TimeStr.from_val(v).val == v


def test_timestr_name() -> None:
    assert TimeStr(value="2000/1/1").name == "AD"
    assert TimeStr(value="2000/1/1@XXX").name == "XXX"


def test_timestr_without_name() -> None:
    assert TimeStr(value="2000/1/1").without_name == "2000/1/1"
    assert TimeStr(value="2000/1/1@XXX").without_name == "2000/1/1"
