import pytest

from knowde._feature._shared.errors.domain import AlreadyExistsError
from knowde._feature.timeline.domain.domain import Time
from knowde._feature.timeline.repo.repo import add_timeline, add_year


def test_add_timeline() -> None:
    """重複はエラー."""
    add_timeline("xxx")
    with pytest.raises(AlreadyExistsError):
        add_timeline("xxx")


def test_add_year() -> None:
    """TLに年を追加."""
    add_timeline("xxx")
    y = add_year("xxx", 2024)
    with pytest.raises(AlreadyExistsError):
        add_year("xxx", 2024)
    assert y == Time(name="xxx", year=2024)


# def test_add_yyyymmdd() -> None:
#     ad = add_timeline("A.D.")  # Anno Domini 主の年に
#     t = add_time("A.D.", 1999, 1, 1)
