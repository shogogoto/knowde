"""person label."""
from neomodel import StringProperty

from knowde._feature._shared.domain.domain import Entity
from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.rel import RelUtil
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.timeline.repo.label import LTime


class LPerson(LBase):
    """person neomodel label."""

    __label__ = "Person"
    # __abstract_node__ = True
    name = StringProperty(index=True, required=True)


class PersonMapper(Entity, frozen=True):
    """人物のORM."""

    name: str


PersonUtil = LabelUtil(label=LPerson, model=PersonMapper)

REL_BIRTH = "BIRTH"
REL_DEATH = "DEATH"
RelBirthUtil = RelUtil(t_source=LPerson, t_target=LTime, name=REL_BIRTH)
RelDeathUtil = RelUtil(t_source=LPerson, t_target=LTime, name=REL_DEATH)

# MEMO: 西暦紀元後 = AD = Anno Domini = 主の年に
SOCIETY_TIMELINE = "AD"
