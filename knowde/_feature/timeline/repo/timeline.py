from __future__ import annotations

from typing import Any

import networkx as nx

from knowde._feature._shared.errors.domain import MultiHitError, NeomodelNotFoundError
from knowde._feature._shared.repo.query import query_cypher
from knowde._feature._shared.repo.rel import dict2query_literal
from knowde._feature.timeline.domain.domain import (
    Day,
    Month,
    Timeline,
    TimelineRoot,
    Year,
)


def _valid_edge(tpl: tuple[Any, Any]) -> bool:
    return tpl[0] is not None and tpl[1] is not None


def list_timeline(
    name: str,
    year: int | None = None,
    month: int | None = None,
) -> Timeline:
    """Get batch days."""
    yw = "" if year is None else dict2query_literal({"value": year})
    mw = "" if month is None else dict2query_literal({"value": month})

    res = query_cypher(
        f"""
        MATCH (tl:Timeline {{name: $name}})
        OPTIONAL MATCH (tl)-[:YEAR]->(y:Year{yw})
        OPTIONAL MATCH (y)-[:MONTH]->(m:Month{mw})
        OPTIONAL MATCH (m)-[:DAY]->(d:Day)
        RETURN tl, y, m, d
        """,
        params={"name": name},
    )
    g = nx.DiGraph()
    roots = set(res.get("tl", convert=TimelineRoot.to_model))
    length = len(roots)
    if length == 0:
        msg = f"時系列'{name}'が見つかりませんでした"
        raise NeomodelNotFoundError(msg)
    if length >= 2:  # noqa: PLR2004
        raise MultiHitError
    tl = next(iter(roots))
    for _y, _m, _d in res.zip("y", "m", "d"):
        y = Year.to_model(_y) if _y is not None else None
        m = Month.to_model(_m) if _m is not None else None
        d = Day.to_model(_d) if _d is not None else None
        pairs = [(tl, y), (y, m), (m, d)]
        g.add_edges_from([p for p in pairs if _valid_edge(p)])
    return Timeline(root=tl, g=g)
