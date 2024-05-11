from knowde._feature.person.domain import AuthorParam, LifeDate, OptionalAuthorParam
from knowde._feature.person.repo.author import (
    add_author,
    change_author,
    find_author_by_name,
    list_authors,
    remove_author,
)


def test_author_crud() -> None:
    p = AuthorParam(
        name="tanaka taro",
        birth=LifeDate(year=2024, month=1, day=1),
    )

    a1 = add_author(p)
    assert a1 in list_authors()

    OptionalAuthorParam.model_rebuild()
    a2 = change_author(
        a1.valid_uid,
        p=OptionalAuthorParam(
            name="yamada hanako",
            death=LifeDate(year=2024, month=1, day=2),
        ),
    )
    assert a1.valid_uid == a2.valid_uid
    assert a2.name == "yamada hanako"
    assert a2.birth == "20240101"
    assert a2.death == "20240102"
    assert len(find_author_by_name("yamada")) == 1

    remove_author(a2.valid_uid)

    assert len(find_author_by_name("yamada")) == 0
