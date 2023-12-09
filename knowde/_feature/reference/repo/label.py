from neomodel import RelationshipFrom, RelationshipTo, ZeroOrOne

from knowde._feature._shared import LBase
from knowde._feature._shared.repo.util import LabelUtil
from knowde._feature.reference.domain import Reference
from knowde._feature.reference.domain.domain import Author


class LReference(LBase):
    __label__ = "Reference"
    parent = RelationshipTo(
        "LReference",
        "INCLUDED",
        cardinality=ZeroOrOne,
    )
    author = RelationshipFrom("LAuthor", "WROTE")


class LAuthor(LBase):
    __label__ = "Author"


ref_util = LabelUtil(label=LReference, model=Reference)
author_util = LabelUtil(label=LAuthor, model=Author)
