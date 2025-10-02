"""label."""

from neomodel import (
    AsyncRelationshipFrom,
    AsyncRelationshipTo,
    AsyncStructuredNode,
    AsyncZeroOrOne,
    DateTimeProperty,
    IntegerProperty,
)

from knowde.shared.user.label import LUser


class LArchievement(AsyncStructuredNode):
    """成果."""

    __label__ = "Archievement"
    n_char = IntegerProperty()
    n_sentence = IntegerProperty()
    n_resource = IntegerProperty()
    created = DateTimeProperty()

    user = AsyncRelationshipFrom(LUser, "ARCHEIVE", cardinality=AsyncZeroOrOne)
    prev = AsyncRelationshipTo(
        "LArchievement",
        "PREV",
        cardinality=AsyncZeroOrOne,
    )
