"""test."""
import pytest

from knowde.primitive.time.domain.errors import (
    EndBeforeStartError,
    NotEqualTimelineError,
)
from knowde.primitive.time.domain.period import Period


def test_period_from_strs() -> None:  # noqa: D103
    with pytest.raises(EndBeforeStartError):
        Period.from_strs("2000/1/1", "1945/9/15")
    with pytest.raises(NotEqualTimelineError):
        Period.from_strs("2000@XX", "2001@YY")


def test_period_output() -> None:  # noqa: D103
    assert Period.from_strs("2000/1/1", None).output == "AD:2000/1/1~"
    assert Period.from_strs(None, "2000/1/1").output == "AD:~2000/1/1"
    assert Period.from_strs("1000/1", "2000/1").output == "AD:1000/1~2000/1"
