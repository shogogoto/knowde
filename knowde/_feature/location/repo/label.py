from neomodel import StringProperty

from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.rel import RelUtil
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.location.domain import Location


class LLocation(LBase):
    """位置."""

    __label__ = "Location"
    name = StringProperty(index=True)


LocUtil = LabelUtil(label=LLocation, model=Location)
RelL2L = RelUtil(
    t_source=LLocation,
    t_target=LLocation,
    name="IN",
)
