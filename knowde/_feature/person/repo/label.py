from neomodel import StringProperty

from knowde._feature._shared.repo.base import LBase
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.person.domain import Author


class LPerson(LBase):
    __label__ = "Person"
    __abstract_node__ = True
    name = StringProperty(index=True)

    # 別フィーチャーに分離するかも
    # 不明な値がある場合9で埋める e.g. 月と日が不明な場合 20249999
    birth = StringProperty(index=True)
    death = StringProperty(index=True)


class LAuthor(LPerson):
    """Referenceの著者."""

    __label__ = "Author"


AuthorUtil = LabelUtil(label=LAuthor, model=Author)
