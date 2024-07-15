"""person repo."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from more_itertools import collapse

from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.timeline.domain.domain import Timeline, TimelineRoot
from knowde._feature.timeline.repo.fetch import fetch_time
from knowde._feature.timeline.repo.label import TimeUtil
from knowde._feature.timeline.repo.query import build_time_graph
from knowde._feature.timeline.repo.timeline import list_timeline
from knowde.feature.person.domain.lifedate import (
    SOCIETY_TIMELINE,
    LifeDate,
    LifeSpan,
)
from knowde.feature.person.repo.label import (
    LPerson,
    PersonMapper,
    PersonUtil,
    RelBirthUtil,
    RelDeathUtil,
)

if TYPE_CHECKING:
    from uuid import UUID

    from knowde._feature.timeline.domain.domain import Time
    from knowde.feature.person.domain import Person


def add_birth(pl: LPerson, d: LifeDate) -> Time:
    """誕生日追加."""
    t = fetch_time(SOCIETY_TIMELINE, *d.tuple)
    tlb = TimeUtil.find_by_id(t.ymd.valid_uid)
    RelBirthUtil.connect(pl, tlb.label)
    return t


def add_death(pl: LPerson, d: LifeDate) -> Time:
    """命日追加."""
    t = fetch_time(SOCIETY_TIMELINE, *d.tuple)
    tlb = TimeUtil.find_by_id(t.ymd.valid_uid)
    RelDeathUtil.connect(pl, tlb.label)
    return t


def add_person(
    name: str,
    birth: Optional[str] = None,
    death: Optional[str] = None,
) -> Person:
    """Add person."""
    ls = LifeSpan(
        birth=LifeDate.from_str(birth),
        death=LifeDate.from_str(death),
    )
    p = PersonUtil.create(name=name)
    if ls.birth is not None:
        add_birth(p.label, ls.birth)
    if ls.death is not None:
        add_death(p.label, ls.death)
    pm = p.to_model()
    return pm.to_person(ls)


def list_society_tl(
    year: int | None = None,
    month: int | None = None,
) -> Timeline:
    """実社会の時系列."""
    return list_timeline(SOCIETY_TIMELINE, year, month)


def rename_person(uid: UUID, name: str) -> Person:
    """Rename person."""
    res = query_cypher(
        """
        MATCH (p:Person {uid: $uid})
        OPTIONAL MATCH (root:Timeline)-[brel]->+(:Time)<-[:BIRTH]-(p)
        OPTIONAL MATCH (:Timeline)-[drel]->+(:Time)<-[:DEATH]-(p)
        RETURN brel, drel, root
        """,
        params={"uid": uid.hex},
    )
    root = res.get("root", TimelineRoot.to_model)[0]
    gb = build_time_graph(collapse(res.get("brel")))
    gd = build_time_graph(collapse(res.get("drel")))
    tb = Timeline(root=root, g=gb).times[0]
    td = Timeline(root=root, g=gd).times[0]
    m = PersonUtil.change(uid=uid, name=name).to_model()
    return m.to_person(LifeSpan.from_times(tb, td))


def list_person() -> list[Person]:
    """人物一覧."""
    res = query_cypher(
        """
        MATCH (p:Person)
        OPTIONAL MATCH (root:Timeline)-[brel]->+(:Time)<-[:BIRTH]-(p)
        OPTIONAL MATCH (:Timeline)-[drel]->+(:Time)<-[:DEATH]-(p)
        RETURN p, brel, drel, root
        """,
    )
    retvals = []
    root = TimelineRoot.to_model(res.get("root")[0])
    for p, brel, drel in res.zip("p", "brel", "drel"):
        gb = build_time_graph(collapse(brel))
        gd = build_time_graph(collapse(drel))
        tb = Timeline(root=root, g=gb).times[0]
        td = Timeline(root=root, g=gd).times[0]
        m = PersonMapper.to_model(p)
        retvals.append(m.to_person(LifeSpan.from_times(tb, td)))
    return retvals
