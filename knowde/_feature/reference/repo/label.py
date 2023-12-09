from neomodel import RelationshipFrom, RelationshipTo, ZeroOrOne

from knowde._feature._shared import LBase
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.reference.domain import Reference


class LReference(LBase):
    __label__ = "Reference"
    parent = RelationshipTo(
        "LReference",
        "INCLUDED",
        cardinality=ZeroOrOne,
    )
    author = RelationshipFrom("LAuthor", "author")


class LAuthor(LBase):
    __label__ = "Author"


ref_util = LabelUtil(label=LReference, model=Reference)
