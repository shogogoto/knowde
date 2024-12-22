"""子をすべて削除."""
from __future__ import annotations

from typing import Optional

from knowde.primitive.__core__.label_repo.query import query_cypher
from knowde.primitive.__core__.label_repo.rel import dict2query_literal

from .fetch import fetch_time
from .label import DayUtil


def remove_day(name: str, year: int, month: int, day: int) -> None:  # noqa: D103
    t = fetch_time(name, year, month, day)
    DayUtil.delete(t.day.valid_uid)


def q_rm_time(
    name: str,
    year: int | None = None,
    month: int | None = None,
) -> str:
    """共通cypher."""
    yw = "" if year is None else dict2query_literal({"value": year})
    mw = "" if month is None else dict2query_literal({"value": month})
    return f"""
        MATCH (tl:Timeline {{name: '{name}'}})
        OPTIONAL MATCH (tl)-[:YEAR]->(y:Year{yw})
        OPTIONAL MATCH (y)-[:MONTH]->(m:Month{mw})
        OPTIONAL MATCH (m)-[:DAY]->(d:Day)
    """


def remove_month(name: str, year: int, month: int) -> None:
    """Remove batch month ~ days."""
    query_cypher(
        f"""
        {q_rm_time(name, year, month)}
        DETACH DELETE m, d
        """,
    )


def remove_year(
    name: str,
    year: Optional[int] = None,
) -> None:
    """Remove batch year ~ days."""
    query_cypher(
        f"""
        {q_rm_time(name, year)}
        DETACH DELETE y, m, d
        """,
    )


def remove_timeline(name: str) -> None:
    """Remove batch timeline ~ days."""
    query_cypher(
        f"""
        {q_rm_time(name)}
        DETACH DELETE tl, y, m, d
        """,
    )


def remove_time(
    name: str,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
) -> None:
    """Facade."""
    if year is not None:
        remove_year(name, year)
        if month is not None:
            if day is not None:
                remove_day(name, year, month, day)
            else:
                remove_month(name, year, month)
    else:
        remove_timeline(name)
