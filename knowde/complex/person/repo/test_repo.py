"""person repo test."""


import pytest
from pytest_unordered import unordered

from knowde.complex.person.repo.repo import (
    add_person,
    complete_person,
    list_person,
    list_society_tl,
    rename_person,
)
from knowde.primitive.time.domain.errors import EndBeforeStartError
from knowde.primitive.time.domain.timestr import TimeStr


def test_person_birth_death() -> None:
    """誕生日と命日を含めて作成."""
    with pytest.raises(EndBeforeStartError):
        add_person("anonymous", "2000/01/01", "1945/9/15")

    add_person("Taro TANAKA", "2000/01/01", "2050/09/15")
    assert list_society_tl() == unordered(
        [TimeStr(value="2000/1/1").val, TimeStr(value="2050/9/15").val],
    )


def test_rename_person() -> None:
    """人物の名前変更."""
    p1 = add_person("anon", "2000/1/1", "2024/07/21")
    p2 = rename_person(p1.valid_uid, "anon2")
    assert p2.valid_uid == p1.valid_uid
    assert p2.name == "anon2"
    assert p2.lifespan == p1.lifespan
    assert p2.created == p1.created
    assert p2.updated != p1.updated


def test_list() -> None:
    """人物一覧."""
    assert list_person() == []
    p1 = add_person("anon1", "2000/01/01", "2024/07/21")
    assert list_person() == [p1]
    p2 = add_person("anon2", "2000/01/01")
    p3 = add_person("anon3", None, "2024/07/21")
    assert list_person() == unordered([p1, p2, p3])


def test_complete() -> None:
    """補完."""
    p1 = add_person("anono")
    p2 = complete_person(p1.valid_uid.hex)
    assert p1 == p2
