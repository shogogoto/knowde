"""person repo."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from knowde._feature.timeline.repo.fetch import fetch_time
from knowde._feature.timeline.repo.label import TimeUtil
from knowde._feature.timeline.repo.timeline import list_timeline
from knowde.feature.person.domain import Person
from knowde.feature.person.domain.lifedate import DeathBeforeBirthError, LifeDate
from knowde.feature.person.repo.label import (
    SOCIETY_TIMELINE,
    LPerson,
    PersonUtil,
    RelBirthUtil,
    RelDeathUtil,
)

if TYPE_CHECKING:
    from knowde._feature.timeline.domain.domain import Time, Timeline


def add_birth(pl: LPerson, d: LifeDate, tlname: str = SOCIETY_TIMELINE) -> Time:
    """誕生日追加."""
    t = fetch_time(tlname, *d.tuple)
    tlb = TimeUtil.find_by_id(t.ymd.valid_uid)
    RelBirthUtil.connect(pl, tlb.label)
    return t


def add_death(pl: LPerson, d: LifeDate, tlname: str = SOCIETY_TIMELINE) -> Time:
    """命日追加."""
    t = fetch_time(tlname, *d.tuple)
    tlb = TimeUtil.find_by_id(t.ymd.valid_uid)
    RelDeathUtil.connect(pl, tlb.label)
    return t


def add_person(
    name: str,
    birth: Optional[str] = None,
    death: Optional[str] = None,
) -> Person:
    """Add person."""
    p = PersonUtil.create(name=name)
    b = LifeDate.from_str(birth)
    d = LifeDate.from_str(death)

    if b is not None and d is not None and d.value < b.value:
        raise DeathBeforeBirthError
    if b is not None:
        add_birth(p.label, b)
    if d is not None:
        add_death(p.label, d)

    pm = p.to_model()
    return Person(
        name=pm.name,
        created=pm.created,
        updated=pm.updated,
        birth=b,
        death=d,
    )


def list_society_tl(
    year: int | None = None,
    month: int | None = None,
) -> Timeline:
    """実社会の時系列."""
    return list_timeline(SOCIETY_TIMELINE, year, month)


# def rename_person(uid: UUID, name: str) -> Person:
#     """Rename person."""
#     return PersonUtil.change(uid=uid, name=name).to_model()
