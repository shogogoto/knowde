from neomodel import IntegerProperty, StringProperty

from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.rel import RelUtil
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.timeline.domain.domain import Day, Month, TimelineRoot, Year


class LTimeline(LBase):
    """時系列ルート."""

    __label__ = "Timeline"
    name = StringProperty(unique=True)


class LTime(LBase):
    """時間."""

    __abstract_node__ = True
    value = IntegerProperty(required=True)


class LYear(LTime):
    __label__ = "Year"


class LMonth(LTime):
    __label__ = "Month"
    value = IntegerProperty(required=True)


class LDay(LTime):
    __label__ = "Day"
    value = IntegerProperty(required=True)


TLUtil = LabelUtil(label=LTimeline, model=TimelineRoot)
YearUtil = LabelUtil(label=LYear, model=Year)
MonthUtil = LabelUtil(label=LMonth, model=Month)
DayUtil = LabelUtil(label=LDay, model=Day)

RelTL2Y = RelUtil(t_source=LTimeline, t_target=LYear, name="YEAR")
RelY2M = RelUtil(t_source=LYear, t_target=LMonth, name="MONTH")
RelM2D = RelUtil(t_source=LMonth, t_target=LDay, name="DAY")
