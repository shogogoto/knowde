"""person label."""
from neomodel import StringProperty, ZeroOrOne

from knowde._feature._shared.domain.domain import Entity
from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.rel import RelUtil
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.timeline.repo.label import LTime
from knowde.feature.person.domain.lifedate import LifeSpan
from knowde.feature.person.domain.person import Person


class LPerson(LBase):
    """person neomodel label."""

    __label__ = "Person"
    # __abstract_node__ = True
    name = StringProperty(index=True, required=True)


class PersonMapper(Entity, frozen=True):
    """人物のORM."""

    name: str

    def to_person(self, lifespan: LifeSpan) -> Person:
        """Convert."""
        return Person(
            uid=self.valid_uid,
            name=self.name,
            created=self.created,
            updated=self.updated,
            lifespan=lifespan,
        )


PersonUtil = LabelUtil(label=LPerson, model=PersonMapper)

REL_BIRTH = "BIRTH"
REL_DEATH = "DEATH"
RelBirthUtil = RelUtil(
    t_source=LPerson,
    t_target=LTime,
    name=REL_BIRTH,
    cardinality=ZeroOrOne,
)
RelDeathUtil = RelUtil(
    t_source=LPerson,
    t_target=LTime,
    name=REL_DEATH,
    cardinality=ZeroOrOne,
)
