"""event repository."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from more_itertools import collapse

from knowde._feature._shared.errors.domain import CompleteNotFoundError, MultiHitError
from knowde._feature._shared.repo.query import excollapse, query_cypher
from knowde._feature.location.domain import Location
from knowde._feature.location.repo.label import LocUtil
from knowde._feature.time.domain.domain import Timeline, TimelineRoot
from knowde._feature.time.repo.query import build_time_graph
from knowde.feature.event.domain.event import Event  # noqa: TCH001
from knowde.feature.event.repo.label import EventMapper, EventUtil, LEvent, RelWhere
from knowde.feature.event.repo.time import add_event_time

if TYPE_CHECKING:
    from uuid import UUID


def add_event(
    text: str,
    location_uid: UUID | None = None,
    time_uid: UUID | None = None,
) -> Event:
    """何時どこで何が起きたかの記述."""
    ev = EventUtil.create(text=text)
    m = ev.to_model()
    loc = None
    if location_uid is not None:
        loc = LocUtil.find_by_id(uid=location_uid)
        RelWhere.connect(ev.label, loc.label)
        loc = loc.to_model()
    t = None
    if time_uid is not None:
        t = add_event_time(m.valid_uid, time_uid)
    return m.to_domain(loc, t)


def ev_q(var: str = "ev") -> str:
    """共通query."""
    return f"""
        OPTIONAL MATCH (root:Timeline)-[trel]->*(:Time)<-[:WHEN]-({var})
        OPTIONAL MATCH (loc:Location)<-[:WHERE]-({var})
        RETURN {var}, trel, loc, root
    """


def to_event(
    ev: LEvent,
    locs: list[Any],
    roots: list[Any],
    trels: list,
) -> Event:
    """Build Event from query results."""
    m = EventMapper.to_model(ev)
    locs = excollapse(locs, Location.to_model)
    loc = None if len(locs) == 0 else locs[0]
    roots = excollapse(roots, TimelineRoot.to_model)
    root = None if len(roots) == 0 else roots[0]
    t = None
    if len(roots) == 1:
        root = roots[0]
        rels = collapse(trels)
        t = Timeline(root=root, g=build_time_graph(rels)).times[0]
    return m.to_domain(loc, t)


def find_event(uid: UUID) -> Event:
    """Find by event uid."""
    res = query_cypher(
        f"""
        MATCH (ev:Event {{uid: $uid}})
        {ev_q()}
        """,
        params={"uid": uid.hex},
    )
    return to_event(res.get("ev")[0], *res.tuple("loc", "root", "trel"))


def list_event() -> list[Event]:
    """一覧."""
    res = query_cypher(
        f"""
        MATCH (ev:Event)
        {ev_q()}
        """,
    )
    ret = []
    for _ev, _loc, _root, _trel in res.zip("ev", "loc", "root", "trel"):
        ret.append(to_event(_ev, _loc, _root, _trel))
    return ret


def change_event(uid: UUID, text: str) -> Event:
    """出来事の記述を変更."""
    EventUtil.change(uid, text=text)
    return find_event(uid=uid)


def complete_event(pref_uid: str) -> Event:
    """Eventの補完."""
    res = query_cypher(
        f"""
        MATCH (ev:Event WHERE ev.uid STARTS WITH $pref_uid)
        {ev_q()}
        """,
        params={"pref_uid": pref_uid},
    )
    evs = res.get("ev")
    if len(evs) == 0:
        raise CompleteNotFoundError
    if len(evs) > 1:
        raise MultiHitError
    return to_event(evs[0], *res.tuple("loc", "root", "trel"))
