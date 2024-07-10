from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from knowde._feature._shared.domain.domain import jst_now
from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.timeline.domain.domain import Month, Time, TimelineRoot, Year
from knowde._feature.timeline.domain.errors import MonthRangeError
from knowde._feature.timeline.repo.label import (
    LTimeline,
    TLUtil,
)

if TYPE_CHECKING:
    from knowde._feature._shared.repo.label import Label


def fetch_timeline(name: str) -> Label[LTimeline, TimelineRoot]:
    """Get or create timeline."""
    tl = TLUtil.find_one_or_none(name=name)
    if tl is not None:
        return tl
    return TLUtil.create(name=name)


def fetch_year(name: str, year: int) -> Time:
    """Get or create year of the timeline."""
    res = query_cypher(
        """
        MERGE (tl:Timeline {name: $name})
        ON CREATE
            SET tl.created = $now,
                tl.updated = $now,
                tl.uid = $uid
        MERGE (tl)-[:YEAR]->(y:Year {value: $y})
        ON CREATE
            SET y.created = $now,
                y.updated = $now,
                y.uid = $uid2
        RETURN tl, y
        """,
        params={
            "name": name,
            "now": jst_now().timestamp(),
            "uid": uuid4().hex,
            "y": year,
            "uid2": uuid4().hex,
        },
    )
    return Time(
        tl=res.get("tl", convert=TimelineRoot.to_model)[0],
        year=res.get("y", convert=Year.to_model)[0],
    )


def fetch_month(name: str, year: int, month: int) -> Time:
    """Get or create year of the timeline."""
    if month < 1 or month > 12:  # noqa: PLR2004
        msg = f"{month}月は存在しない"
        raise MonthRangeError(msg)
    res = query_cypher(
        """
        MERGE (tl:Timeline {name: $name})
        ON CREATE
            SET tl.created = $now,
                tl.updated = $now,
                tl.uid = $uid
        MERGE (tl)-[:YEAR]->(y:Year {value: $y})
        ON CREATE
            SET y.created = $now,
                y.updated = $now,
                y.uid = $uid2
        MERGE (y)-[:MONTH]->(m:Month {value: $m})
        ON CREATE
            SET m.created = $now,
                m.updated = $now,
                m.uid = $uid3
        RETURN tl, y, m
        """,
        params={
            "name": name,
            "now": jst_now().timestamp(),
            "uid": uuid4().hex,
            "y": year,
            "uid2": uuid4().hex,
            "m": month,
            "uid3": uuid4().hex,
        },
    )
    return Time(
        tl=res.get("tl", convert=TimelineRoot.to_model)[0],
        year=res.get("y", convert=Year.to_model)[0],
        month=res.get("m", convert=Month.to_model)[0],
    )
    # t = fetch_year(name, year)

    # # rels = RelTL2Y.find_by_source_id(t.to_model().valid_uid, {"value": year})
    # # if len(rels) == 0:
    # #     lb = YearUtil.create(value=year)
    # #     RelTL2Y.to(tl.label).connect(lb.label)
    # #     y = lb.to_model()
    # # elif len(rels) == 1:
    # #     y = Year.to_model(rels[0].end_node())
    # # else:
    # #     msg = f"'{name}'に{year}年は既にあります'"
    # #     raise MultiHitError(msg)
    # # return Time(
    # #     tl=tl.to_model(),
    # #     year=y,
    # # )
    # rels = RelY2M
    # return None


# def add_time(name: str, year: int, month: int | None, day: int | None) -> None:
#     """日付を追加."""
#     # if YearUtil.find_one_or_none(value=year):
#     YearUtil.create(value=year)
#     MonthUtil.create(value=month)
#     DayUtil.create(value=day)
