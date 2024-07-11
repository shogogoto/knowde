"""子をすべて削除."""
import pytest
from pytest_unordered import unordered

from knowde._feature._shared.errors.domain import NeomodelNotFoundError
from knowde._feature.timeline.domain.domain import TimeValue
from knowde._feature.timeline.repo.fetch import fetch_time
from knowde._feature.timeline.repo.timeline import list_timeline


def test_list() -> None:
    """月とその月の日を削除."""
    for i in range(1, 4):
        fetch_time("x", 2024, 12, i)
    with pytest.raises(NeomodelNotFoundError):
        list_timeline("y")
    assert list_timeline("x").values == unordered(
        [TimeValue(name="x", year=2024, month=12, day=i) for i in range(1, 4)],
    )
