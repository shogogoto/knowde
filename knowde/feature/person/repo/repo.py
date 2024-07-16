"""person repo."""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Optional

from more_itertools import collapse

from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.timeline.domain.domain import Timeline
from knowde._feature.timeline.repo.fetch import fetch_time
from knowde._feature.timeline.repo.label import TimeUtil
from knowde._feature.timeline.repo.query import build_time_graph
from knowde._feature.timeline.repo.timeline import list_timeline
from knowde.feature.person.domain import Person  # noqa: TCH001
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

    from knowde._feature._shared.repo.base import RelBase
    from knowde._feature.timeline.domain.domain import Time


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


def build_lifespan(
    brels: Iterator[RelBase],
    drels: Iterator[RelBase],
) -> LifeSpan:
    """Time rels to lifespan."""
    root = fetch_time(SOCIETY_TIMELINE).tl
    gb = build_time_graph(brels)
    gd = build_time_graph(drels)
    tb = Timeline(root=root, g=gb).times[0]
    td = Timeline(root=root, g=gd).times[0]
    return LifeSpan.from_times(tb, td)


def complete_person(pref_uid: str) -> Person:
    """補完."""
    res = query_cypher(
        """
        MATCH (p:Person WHERE p.uid STARTS WITH $pref_uid)
        OPTIONAL MATCH (:Timeline)-[brel]->+(:Time)<-[:BIRTH]-(p)
        OPTIONAL MATCH (:Timeline)-[drel]->+(:Time)<-[:DEATH]-(p)
        RETURN p, brel, drel
        """,
        params={"pref_uid": pref_uid},
    )
    m = res.get("p", PersonMapper.to_model)[0]
    ls = build_lifespan(collapse(res.get("brel")), collapse(res.get("drel")))
    return m.to_person(ls)


def find_person_by_id(uid: UUID) -> Person:
    """Find by uuid."""
    res = query_cypher(
        """
        MATCH (p:Person {uid: $uid})
        OPTIONAL MATCH (root:Timeline)-[brel]->+(:Time)<-[:BIRTH]-(p)
        OPTIONAL MATCH (:Timeline)-[drel]->+(:Time)<-[:DEATH]-(p)
        RETURN p, brel, drel, root
        """,
        params={"uid": uid.hex},
    )
    m = res.get("p", PersonMapper.to_model)[0]
    ls = build_lifespan(collapse(res.get("brel")), collapse(res.get("drel")))
    return m.to_person(ls)


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
    ls = build_lifespan(collapse(res.get("brel")), collapse(res.get("drel")))
    m = PersonUtil.change(uid=uid, name=name).to_model()
    return m.to_person(ls)


def list_person() -> list[Person]:
    """人物一覧."""
    root = fetch_time(SOCIETY_TIMELINE).tl
    res = query_cypher(
        """
        MATCH (p:Person)
        OPTIONAL MATCH (:Timeline)-[brel]->+(:Time)<-[:BIRTH]-(p)
        OPTIONAL MATCH (:Timeline)-[drel]->+(:Time)<-[:DEATH]-(p)
        RETURN p, brel, drel
        """,
    )
    retvals = []
    for p, brel, drel in res.zip("p", "brel", "drel"):
        gb = build_time_graph(collapse(brel))
        gd = build_time_graph(collapse(drel))
        tb = Timeline(root=root, g=gb).times[0]
        td = Timeline(root=root, g=gd).times[0]
        m = PersonMapper.to_model(p)
        retvals.append(m.to_person(LifeSpan.from_times(tb, td)))
    return retvals
