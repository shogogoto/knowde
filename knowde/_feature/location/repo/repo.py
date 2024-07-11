from uuid import UUID

from knowde._feature.location.domain import Location
from knowde._feature.location.repo.label import LocUtil, RelL2L


def add_location_root(name: str) -> Location:
    return LocUtil.create(name=name).to_model()


def add_sub_location(uid: UUID, name: str) -> Location:
    parent = LocUtil.fetch(uid=uid)
    sub = LocUtil.fetch(name=name)
    RelL2L.connect(parent.label, sub.label)
    return sub.to_model()


def remove_location(uid: UUID) -> None:
    LocUtil.delete(uid=uid)
