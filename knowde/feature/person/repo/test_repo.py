"""person repo test."""


import pytest
from pytest_unordered import unordered

from knowde.feature.person.domain.lifedate import DeathBeforeBirthError, t_society
from knowde.feature.person.repo.repo import add_person, list_society_tl


def test_person_birth_death() -> None:
    """誕生日と命日を含めて作成."""
    with pytest.raises(DeathBeforeBirthError):
        add_person("Taro TANAKA", "20000101", "19450915")

    add_person("Taro TANAKA", "20000101", "20500915")
    assert list_society_tl().values == unordered(
        [t_society(2000, 1, 1), t_society(2050, 9, 15)],
    )
