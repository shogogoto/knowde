"""test."""
import pytest

from .domain import validate_ymd
from .errors import InvalidTimeYMDError


def test_validate_ymd() -> None:  # noqa: D103
    validate_ymd(1, 1, 1)
    with pytest.raises(InvalidTimeYMDError):
        validate_ymd(None, 1, 1)
    with pytest.raises(InvalidTimeYMDError):
        validate_ymd(1, None, 1)
    validate_ymd(1, 1, None)
    validate_ymd(1, None, None)
    with pytest.raises(InvalidTimeYMDError):
        validate_ymd(None, 1, None)
    with pytest.raises(InvalidTimeYMDError):
        validate_ymd(None, None, 1)
    validate_ymd(None, None, None)
