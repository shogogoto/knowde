"""person label."""
from neomodel import StringProperty, ZeroOrOne

from knowde.complex.person.domain.person import Person
from knowde.core.domain.domain import Entity
from knowde.core.label_repo.base import LBase
from knowde.core.label_repo.rel import RelUtil
from knowde.core.label_repo.util import LabelUtil
from knowde.primitive.time.domain.period import Period
from knowde.primitive.time.repo.label import LTime


class LPerson(LBase):
    """person neomodel label."""

    __label__ = "Person"
    # __abstract_node__ = True
    name = StringProperty(index=True, required=True)


class PersonMapper(Entity, frozen=True):
    """人物のORM."""

    name: str

    def to_person(self, period: Period) -> Person:
        """Convert."""
        return Person(
            uid=self.valid_uid,
            name=self.name,
            created=self.created,
            updated=self.updated,
            lifespan=period,
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
