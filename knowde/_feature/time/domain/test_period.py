import pytest

from knowde._feature.time.domain.errors import (
    EmptyPeriodError,
    EndBeforeStartError,
    NotEqualTimelineError,
)
from knowde._feature.time.domain.period import Period


def test_period_from_strs() -> None:
    with pytest.raises(EndBeforeStartError):
        Period.from_strs("2000/1/1", "1945/9/15")
    with pytest.raises(NotEqualTimelineError):
        Period.from_strs("2000@XX", "2001@YY")
    with pytest.raises(EmptyPeriodError):
        Period.from_strs(None, None)


def test_period_output() -> None:
    assert Period.from_strs("2000/1/1", None).output == "AD:2000/1/1~"
    assert Period.from_strs(None, "2000/1/1").output == "AD:~2000/1/1"
    assert Period.from_strs("1000/1", "2000/1").output == "AD:1000/1~2000/1"
