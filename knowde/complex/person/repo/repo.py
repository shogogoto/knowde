"""person repo."""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Optional

from more_itertools import collapse

from knowde.complex.person.domain import Person
from knowde.complex.person.repo.label import (
    LPerson,
    PersonMapper,
    PersonUtil,
    RelBirthUtil,
    RelDeathUtil,
)
from knowde.core.label_repo.query import query_cypher
from knowde.primitive.time.domain.const import SOCIETY_TIMELINE
from knowde.primitive.time.domain.domain import Timeline, TimeValue
from knowde.primitive.time.domain.period import Period
from knowde.primitive.time.repo.fetch import fetch_time
from knowde.primitive.time.repo.label import TimeUtil
from knowde.primitive.time.repo.query import build_time_graph
from knowde.primitive.time.repo.timeline import list_time

if TYPE_CHECKING:
    from uuid import UUID

    from knowde.core.label_repo.base import RelBase
    from knowde.primitive.time.domain.domain import Time


def add_birth(pl: LPerson, v: TimeValue) -> Time:
    """誕生日追加."""
    t = fetch_time(SOCIETY_TIMELINE, *v.ymd_tuple)
    tlb = TimeUtil.find_by_id(t.leaf.valid_uid)
    RelBirthUtil.connect(pl, tlb.label)
    return t


def add_death(pl: LPerson, v: TimeValue) -> Time:
    """命日追加."""
    t = fetch_time(SOCIETY_TIMELINE, *v.ymd_tuple)
    tlb = TimeUtil.find_by_id(t.leaf.valid_uid)
    RelDeathUtil.connect(pl, tlb.label)
    return t


def add_person(
    name: str,
    birth: Optional[str] = None,
    death: Optional[str] = None,
) -> Person:
    """Add person."""
    period = Period.from_strs(birth, death)
    p = PersonUtil.create(name=name)
    if period.start is not None:
        add_birth(p.label, period.start)
    if period.end is not None:
        add_death(p.label, period.end)
    pm = p.to_model()
    return pm.to_person(period)


def list_society_tl(
    year: int | None = None,
    month: int | None = None,
) -> list[TimeValue]:
    """実社会の時系列."""
    return list_time(SOCIETY_TIMELINE, year, month)


def build_period(
    brels: Iterator[RelBase],
    drels: Iterator[RelBase],
) -> Period:
    """Time rels to lifespan."""
    root = fetch_time(SOCIETY_TIMELINE).tl
    gb = build_time_graph(brels)
    gd = build_time_graph(drels)
    tb = Timeline(root=root, g=gb).times[0]
    td = Timeline(root=root, g=gd).times[0]
    return Period.from_times(tb, td)


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
    ls = build_period(collapse(res.get("brel")), collapse(res.get("drel")))
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
    ls = build_period(collapse(res.get("brel")), collapse(res.get("drel")))
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
    ls = build_period(collapse(res.get("brel")), collapse(res.get("drel")))
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
        retvals.append(m.to_person(Period.from_times(tb, td)))
    return retvals
