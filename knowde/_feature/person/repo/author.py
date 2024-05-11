from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature.person.domain import LifeDate
from knowde._feature.person.repo.label import AuthorUtil

if TYPE_CHECKING:
    from uuid import UUID

    from knowde._feature.person.domain import Author, AuthorParam, OptionalAuthorParam


def add_author(p: AuthorParam) -> Author:
    """同姓同名はあり得るので特に制約はなし."""
    birth = None if p.birth is None else p.birth.to_str()
    death = None if p.death is None else p.death.to_str()
    return AuthorUtil.create(
        name=p.name,
        birth=birth,
        death=death,
    ).to_model()


def list_authors() -> list[Author]:
    return AuthorUtil.find().to_model()


def find_author_by_name(name: str) -> list[Author]:
    return AuthorUtil.find(name__contains=name).to_model()


def change_author(uid: UUID, p: OptionalAuthorParam) -> Author:
    d = p.model_dump()
    if isinstance(p.birth, LifeDate):
        d["birth"] = p.birth.to_str()
    if isinstance(p.death, LifeDate):
        d["death"] = p.death.to_str()
    return AuthorUtil.change(uid=uid, **d).to_model()


def remove_author(uid: UUID) -> None:
    one = AuthorUtil.find_by_id(uid).to_model()
    AuthorUtil.delete(one.valid_uid)
