from __future__ import annotations

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
        OPTIONAL MATCH (tl)-[yrel:YEAR]->(y:Year{yw})
        OPTIONAL MATCH (y)-[mrel:MONTH]->(m:Month{mw})
        OPTIONAL MATCH (m)-[drel:DAY]->(d:Day)
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
    # for tl, _y, _m, _d in zip(*res.tuple("y", "m", "d")):
    for _y, _m, _d in res.zip("y", "m", "d"):
        y = Year.to_model(_y)
        m = Month.to_model(_m)
        d = Day.to_model(_d)
        g.add_edges_from([(tl, y), (y, m), (m, d)])
    return Timeline(root=tl, g=g)
