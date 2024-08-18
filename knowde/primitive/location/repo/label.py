"""location label."""
from neomodel import StringProperty

from knowde.core.repo.base import LBase
from knowde.core.repo.rel import RelUtil
from knowde.core.repo.util import LabelUtil
from knowde.primitive.location.domain import Location


class LLocation(LBase):
    """位置."""

    __label__ = "Location"
    name = StringProperty(index=True, required=True)


REL_L2L_NAME = "INCLUDE"

LocUtil = LabelUtil(label=LLocation, model=Location)
RelL2L = RelUtil(
    t_source=LLocation,
    t_target=LLocation,
    name=REL_L2L_NAME,
)
