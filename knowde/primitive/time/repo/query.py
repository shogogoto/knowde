"""複雑なクエリ."""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

import networkx as nx
from more_itertools import collapse

from knowde.primitive.__core__.label_repo.query import query_cypher
from knowde.primitive.time.domain.domain import (
    Day,
    Month,
    Timeline,
    TimelineRoot,
    Year,
)

from .label import LMonth, LTimeline, LYear

if TYPE_CHECKING:
    from uuid import UUID

    from knowde.primitive.__core__.label_repo.base import RelBase
    from knowde.primitive.time.domain.domain import Time


def build_time_graph(rels: Iterator[RelBase]) -> nx.DiGraph:
    """複数関係をグラフへ変換."""
    g = nx.DiGraph()
    for rel in rels:
        if rel is None:
            continue
        s = rel.start_node()
        e = rel.end_node()
        if isinstance(s, LTimeline):
            root = TimelineRoot.to_model(s)
            y = Year.to_model(e)
            g.add_edge(root, y)
        elif isinstance(s, LYear):
            y = Year.to_model(s)
            m = Month.to_model(e)
            g.add_edge(y, m)
        elif isinstance(s, LMonth):
            m = Month.to_model(s)
            d = Day.to_model(e)
            g.add_edge(m, d)
    return g


def find_times_from(name: str, uid: UUID) -> list[Time]:
    """timelineに繋がるNodeのuidからtimeを検索."""
    res = query_cypher(
        """
        MATCH (root:Timeline {name: $name})
        OPTIONAL MATCH (root)-[rel]->+({uid: $uid})
        RETURN root, rel
        """,
        params={"name": name, "uid": uid.hex},
    )
    root = res.get("root", TimelineRoot.to_model)[0]
    rels = collapse(res.get("rel"))
    return Timeline(root=root, g=build_time_graph(rels)).times
