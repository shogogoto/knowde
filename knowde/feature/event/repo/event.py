"""event repository."""
from __future__ import annotations

from typing import TYPE_CHECKING

from more_itertools import collapse

from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.location.domain import Location
from knowde._feature.location.repo.label import LocUtil
from knowde._feature.timeline.domain.domain import Timeline, TimelineRoot
from knowde._feature.timeline.repo.query import build_time_graph, find_times_from
from knowde.feature.event.repo.label import EventMapper, EventUtil, RelWhere
from knowde.feature.event.repo.time import add_event_time
from knowde.feature.person.domain.lifedate import SOCIETY_TIMELINE

if TYPE_CHECKING:
    from uuid import UUID

    from knowde.feature.event.domain.event import Event


def add_event(
    text: str,
    location_uid: UUID | None = None,
    time_uid: UUID | None = None,
    timeline: str = SOCIETY_TIMELINE,
) -> Event:
    """何時どこで何が起きたかの記述."""
    ev = EventUtil.create(text=text)
    m = ev.to_model()
    loc = None
    t = None
    if location_uid is not None:
        loc = LocUtil.find_by_id(uid=location_uid)
        RelWhere.connect(ev.label, loc.label)
        loc = loc.to_model()
    if time_uid is not None:
        ymd = find_times_from(timeline, time_uid)[0].leaf
        t = add_event_time(m.valid_uid, ymd.valid_uid)
    return m.to_domain(loc, t)


def find_event(uid: UUID) -> None:
    """Find by event uid."""
    res = query_cypher(
        """
        MATCH (ev:Event {uid: $uid})
        OPTIONAL MATCH (root:Timeline)-[trel]->*(:Time)<-[:WHEN]-(ev)
        OPTIONAL MATCH (loc:Location)<-[:WHERE]-(ev)
        RETURN ev, trel, loc, root
        """,
        params={"uid": uid.hex},
    )
    m = res.get("ev", EventMapper.to_model)[0]
    loc = res.get("loc", Location.to_model)[0]
    roots = res.get("root", TimelineRoot.to_model)
    t = None
    if len(roots) == 1:
        root = roots[0]
        rels = collapse(res.get("trel"))
        t = Timeline(root=root, g=build_time_graph(rels)).times[0]
    return m.to_domain(loc, t)
