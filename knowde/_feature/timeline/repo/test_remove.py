import pytest

from knowde._feature._shared.errors.domain import NeomodelNotFoundError
from knowde._feature.timeline.domain.domain import TimeValue
from knowde._feature.timeline.repo.fetch import fetch_time
from knowde._feature.timeline.repo.remove import (
    remove_month,
    remove_timeline,
    remove_year,
)
from knowde._feature.timeline.repo.timeline import list_timeline


def test_remove_month() -> None:
    """月とその配下の日を削除."""
    for i in range(1, 4):
        fetch_time("x", 2024, 12, i)
        fetch_time("x", 2024, 11, i)
    assert len(list_timeline("x", 2024).values) == 6  # noqa: PLR2004
    remove_month("x", 2024, 12)
    assert len(list_timeline("x", 2024).values) == 3  # noqa: PLR2004


def test_remove_year() -> None:
    """年とその配下の月日を削除."""
    for i in range(1, 4):
        fetch_time("x", 2024, i, i)
        fetch_time("x", 2025, i, i)
    assert len(list_timeline("x", 2024).values) == 3  # noqa: PLR2004
    assert len(list_timeline("x", 2025).values) == 3  # noqa: PLR2004
    remove_year("x", 2024)
    assert list_timeline("x", 2024).values == [TimeValue(name="x")]
    assert len(list_timeline("x", 2025).values) == 3  # noqa: PLR2004


def test_remove_timeline() -> None:
    """年とその配下の月日を削除."""
    for i in range(1, 4):
        fetch_time("x", 2024, i, i)
        fetch_time("x", 2025, i, i)
    assert len(list_timeline("x").values) == 6  # noqa: PLR2004
    remove_timeline("x")
    with pytest.raises(NeomodelNotFoundError):
        list_timeline("x")
