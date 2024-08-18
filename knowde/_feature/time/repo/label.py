from neomodel import IntegerProperty, StringProperty

from knowde._feature.time.domain.domain import YMD, Day, Month, TimelineRoot, Year
from knowde.core.repo.base import LBase
from knowde.core.repo.rel import RelUtil
from knowde.core.repo.util import LabelUtil


class LTimeline(LBase):
    """時系列ルート."""

    __label__ = "Timeline"
    name = StringProperty(unique=True)


class LTime(LBase):
    """時間."""

    __label__ = "Time"
    __abstract_node__ = True
    value = IntegerProperty(required=True)


class LYear(LTime):
    # __optional_labels__ = ["Time"]
    __label__ = "Year"


class LMonth(LTime):
    # __optional_labels__ = ["Time"]
    __label__ = "Month"


class LDay(LTime):
    # __optional_labels__ = ["Time"]
    __label__ = "Day"


TLUtil = LabelUtil(label=LTimeline, model=TimelineRoot)
TimeUtil = LabelUtil(label=LTime, model=YMD)
YearUtil = LabelUtil(label=LYear, model=Year)
MonthUtil = LabelUtil(label=LMonth, model=Month)
DayUtil = LabelUtil(label=LDay, model=Day)

RelTL2Y = RelUtil(t_source=LTimeline, t_target=LYear, name="YEAR")
RelY2M = RelUtil(t_source=LYear, t_target=LMonth, name="MONTH")
RelM2D = RelUtil(t_source=LMonth, t_target=LDay, name="DAY")
