import pytest

from knowde._feature.timeline.domain.domain import validate_ymd
from knowde._feature.timeline.domain.errors import InvalidTimeYMDError


def test_validate_ymd() -> None:
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
