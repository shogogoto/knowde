from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from knowde._feature._shared.domain.domain import jst_now
from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.timeline.domain.domain import Day, Month, Time, TimelineRoot, Year
from knowde._feature.timeline.domain.errors import DayRangeError, MonthRangeError
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
                tl.uid = $uid_tl
        MERGE (tl)-[:YEAR]->(y:Year {value: $y})
        ON CREATE
            SET y.created = $now,
                y.updated = $now,
                y.uid = $uid_y
        RETURN tl, y
        """,
        params={
            "name": name,
            "now": jst_now().timestamp(),
            "uid_tl": uuid4().hex,
            "y": year,
            "uid_y": uuid4().hex,
        },
    )
    return Time(
        tl=res.get("tl", convert=TimelineRoot.to_model)[0],
        year=res.get("y", convert=Year.to_model)[0],
    )


def fetch_month(name: str, year: int, month: int) -> Time:
    """Get or create year and month of the timeline."""
    if month < 1 or month > 12:  # noqa: PLR2004
        msg = f"{month}月は存在しない"
        raise MonthRangeError(msg)
    t = fetch_year(name, year)
    res = query_cypher(
        """
        MERGE (y:Year {uid: $uid_y})-[:MONTH]->(m:Month {value: $m})
        ON CREATE
            SET m.created = $now,
                m.updated = $now,
                m.uid = $uid_m
        RETURN m
        """,
        params={
            "now": jst_now().timestamp(),
            "uid_y": t.year.valid_uid.hex,
            "m": month,
            "uid_m": uuid4().hex,
        },
    )
    return Time(
        tl=t.tl,
        year=t.year,
        month=res.get("m", convert=Month.to_model)[0],
    )


def fetch_day(name: str, year: int, month: int, day: int) -> Time:
    """Get or create year~day of the timeline."""
    if day < 1 or day > 31:  # noqa: PLR2004
        msg = f"{month}日は存在しない"
        raise DayRangeError(msg)
    t = fetch_month(name, year, month)
    res = query_cypher(
        """
        MERGE (m:Month {uid: $uid_m})-[:DAY]->(d:Day {value: $d})
        ON CREATE
            SET d.created = $now,
                d.updated = $now,
                d.uid = $uid_d
        RETURN d
        """,
        params={
            "now": jst_now().timestamp(),
            "uid_m": t.year.valid_uid.hex,
            "d": day,
            "uid_d": uuid4().hex,
        },
    )
    return Time(
        tl=t.tl,
        year=t.year,
        month=t.month,
        day=res.get("d", convert=Day.to_model)[0],
    )


# def add_time(name: str, year: int, month: int | None, day: int | None) -> None:
#     """日付を追加."""
#     # if YearUtil.find_one_or_none(value=year):
#     YearUtil.create(value=year)
#     MonthUtil.create(value=month)
#     DayUtil.create(value=day)
