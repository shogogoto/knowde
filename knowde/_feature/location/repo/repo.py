from uuid import UUID

from knowde._feature.location.domain import Location
from knowde._feature.location.repo.label import LocUtil


def add_location_root(name: str) -> Location:
    return LocUtil.create(name=name).to_model()


def add_sub_location(_uid: UUID, _name: str) -> None:
    pass


def remove_location(uid: UUID) -> None:
    LocUtil.delete(uid=uid)
