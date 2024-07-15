"""person repo test."""


import pytest
from pytest_unordered import unordered

from knowde.feature.person.domain.lifedate import DeathBeforeBirthError, t_society
from knowde.feature.person.repo.repo import (
    add_person,
    list_person,
    list_society_tl,
    rename_person,
)


def test_person_birth_death() -> None:
    """誕生日と命日を含めて作成."""
    with pytest.raises(DeathBeforeBirthError):
        add_person("anonymous", "20000101", "19450915")

    add_person("Taro TANAKA", "20000101", "20500915")
    assert list_society_tl().values == unordered(
        [t_society(2000, 1, 1), t_society(2050, 9, 15)],
    )


def test_rename_person() -> None:
    """人物の名前変更."""
    p1 = add_person("anon", "20000101", "20240721")
    p2 = rename_person(p1.valid_uid, "anon2")
    assert p2.valid_uid == p1.valid_uid
    assert p2.name == "anon2"
    assert p2.lifespan == p1.lifespan
    assert p2.created == p1.created
    assert p2.updated != p1.updated


def test_list() -> None:
    """人物一覧."""
    assert list_person() == []
    p1 = add_person("anon1", "20000101", "20240721")
    assert list_person() == [p1]
    p2 = add_person("anon2", "20000101")
    p3 = add_person("anon3", None, "20240721")
    assert list_person() == unordered([p1, p2, p3])
