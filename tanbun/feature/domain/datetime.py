"""日時に関する共通の型と変換."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

import neo4j
import pytz
from pydantic import BeforeValidator

TZ = pytz.timezone("Asia/Tokyo")  # pytz じゃないとneo4j driverには対応していないっぽい


def neo4j_dt_validator(v: Any) -> datetime:
    """neo4j.time.DateTimeをdatetime.datetimeに変換する."""
    if isinstance(v, neo4j.time.DateTime):
        return neo4j.time.DateTime.to_native(v)
    return v


type Neo4jDateTime = Annotated[datetime, BeforeValidator(neo4j_dt_validator)]
