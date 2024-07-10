from __future__ import annotations

from typing import TYPE_CHECKING

from knowde._feature._shared.errors.domain import AlreadyExistsError
from knowde._feature.timeline.domain.domain import Time
from knowde._feature.timeline.repo.label import (
    RelTL2Y,
    TLUtil,
    YearUtil,
)

if TYPE_CHECKING:
    from knowde._feature.timeline.domain.domain import TimelineRoot


def add_timeline(name: str) -> TimelineRoot:
    """時系列ルート作成."""
    tl = TLUtil.find_one_or_none(name=name)
    if tl is not None:
        msg = f"時系列'{name}'は既に存在しています'"
        raise AlreadyExistsError(msg)
    return TLUtil.create(name=name).to_model()


def add_year(name: str, year: int) -> Time:
    tl = TLUtil.find_one(name=name)
    rels = RelTL2Y.find_by_source_id(tl.to_model().valid_uid, {"value": year})
    if len(rels) > 0:
        msg = f"'{name}'に{year}年は既にあります'"
        raise AlreadyExistsError(msg)
    y = YearUtil.create(value=year)
    RelTL2Y.to(tl.label).connect(y.label)
    return Time(
        name=tl.to_model().name,
        year=y.to_model().value,
        # month=None,
        # day=None,
    )


# def add_time(name: str, year: int, month: int | None, day: int | None) -> None:
#     """日付を追加."""
#     # if YearUtil.find_one_or_none(value=year):
#     YearUtil.create(value=year)
#     MonthUtil.create(value=month)
#     DayUtil.create(value=day)
