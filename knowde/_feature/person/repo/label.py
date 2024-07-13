from neomodel import StringProperty

from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.person.domain import Person


class LPerson(LBase):
    __label__ = "Person"
    # __abstract_node__ = True
    name = StringProperty(index=True, required=True)


PersonUtil = LabelUtil(label=LPerson, model=Person)
