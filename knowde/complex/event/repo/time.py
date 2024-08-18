"""time related repo."""
from __future__ import annotations

from typing import TYPE_CHECKING

from more_itertools import collapse

from knowde._feature.time.domain.domain import Timeline, TimelineRoot
from knowde._feature.time.repo.query import build_time_graph
from knowde.core.repo.query import query_cypher

if TYPE_CHECKING:
    from uuid import UUID

    from knowde._feature.time.domain.domain import Time


def add_event_time(ev_uid: UUID, t_uid: UUID) -> Time:
    """イベント日時作成."""
    res = query_cypher(
        """
        MATCH (ev:Event {uid: $ev_uid}),
            (t {uid: $t_uid})
        CREATE (ev)-[:WHEN]->(t)
        WITH t
        OPTIONAL MATCH (root:Timeline)-[rel]->*(t)
        RETURN root, rel
        """,
        params={"ev_uid": ev_uid.hex, "t_uid": t_uid.hex},
    )
    root = res.get("root", TimelineRoot.to_model)[0]
    rels = collapse(res.get("rel"))
    return Timeline(root=root, g=build_time_graph(rels)).times[0]
