from uuid import UUID

from knowde._feature.person.domain import Person
from knowde._feature.person.repo.label import PersonUtil


def add_person(name: str) -> Person:
    return PersonUtil.create(name=name).to_model()


def rename_person(uid: UUID, name: str) -> Person:
    return PersonUtil.change(uid=uid, name=name).to_model()
