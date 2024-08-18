from __future__ import annotations

from uuid import uuid4

from knowde._feature.time.domain.domain import (
    Day,
    Month,
    Time,
    TimelineRoot,
    Year,
)
from knowde._feature.time.domain.errors import DayRangeError, MonthRangeError
from knowde.core import jst_now
from knowde.core.repo.query import query_cypher

from .label import TLUtil


def fetch_timeline(name: str) -> Time:
    """Get or create timeline."""
    tl = TLUtil.fetch(name=name)
    return Time(tl=tl.to_model())


def fetch_year(name: str, year: int) -> Time:
    """Get or create year of the timeline."""
    res = query_cypher(
        """
        MERGE (tl:Timeline {name: $name})
        ON CREATE
            SET tl.created = $now,
                tl.updated = $now,
                tl.uid = $uid_tl
        MERGE (tl)-[:YEAR]->(y:Year:Time {value: $y})
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
        y=res.get("y", convert=Year.to_model)[0],
    )


def fetch_month(name: str, year: int, month: int) -> Time:
    """Get or create year and month of the timeline."""
    if month < 1 or month > 12:  # noqa: PLR2004
        msg = f"{month}月は存在しない"
        raise MonthRangeError(msg)
    t = fetch_year(name, year)
    res = query_cypher(
        """
        MATCH (y:Year {uid: $uid_y})
        MERGE (y)-[:MONTH]->(m:Month:Time {value: $m})
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
        y=t.y,
        m=res.get("m", convert=Month.to_model)[0],
    )


def fetch_day(name: str, year: int, month: int, day: int) -> Time:
    """Get or create year~day of the timeline."""
    if day < 1 or day > 31:  # noqa: PLR2004
        msg = f"{month}月{day}日は存在しない"
        raise DayRangeError(msg)
    t = fetch_month(name, year, month)
    res = query_cypher(
        """
        MATCH (m:Month {uid: $uid_m})
        MERGE (m)-[:DAY]->(d:Day:Time {value: $d})
        ON CREATE
            SET d.created = $now,
                d.updated = $now,
                d.uid = $uid_d
        RETURN d
        """,
        params={
            "now": jst_now().timestamp(),
            "uid_m": t.month.valid_uid.hex,
            "d": day,
            "uid_d": uuid4().hex,
        },
    )
    return Time(
        tl=t.tl,
        y=t.y,
        m=t.m,
        d=res.get("d", convert=Day.to_model)[0],
    )


def fetch_time(
    name: str,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
) -> Time:
    """日付取得のfacade."""
    if year is None:
        if month is not None or day is not None:
            msg = "年なしで月日をしていできません"
            raise ValueError(msg)
        return fetch_timeline(name)

    if month is None:
        if day is not None:
            msg = "月なしで日を指定できません"
            raise ValueError(msg)
        return fetch_year(name, year)
    if day is None:
        return fetch_month(name, year, month)
    return fetch_day(name, year, month, day)
