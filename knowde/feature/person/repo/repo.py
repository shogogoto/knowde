"""person repo."""
from uuid import UUID

from knowde.feature.person.domain import Person
from knowde.feature.person.repo.label import PersonUtil


def add_person(name: str) -> Person:
    """Add person."""
    return PersonUtil.create(name=name).to_model()


def rename_person(uid: UUID, name: str) -> Person:
    """Rename person."""
    return PersonUtil.change(uid=uid, name=name).to_model()
