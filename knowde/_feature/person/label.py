from neomodel import DateProperty, StringProperty

from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.person.domain import Author


class LPerson(LBase):
    __label__ = "Person"
    __abstract_node__ = True
    name = StringProperty(index=True)

    # TimeLineに分離するかも
    birth = DateProperty(index=True)
    death = DateProperty(index=True)


class LAuthor(LPerson):
    """Referenceの著者."""

    __label__ = "Author"


AuthorUtil = LabelUtil(label=LAuthor, model=Author)
