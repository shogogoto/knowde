"""label."""

from neomodel import (
    AsyncRelationshipFrom,
    AsyncRelationshipTo,
    AsyncStructuredNode,
    AsyncZeroOrOne,
    DateTimeNeo4jFormatProperty,
    IntegerProperty,
)

from knowde.shared.user.label import LUser


class LArchievement(AsyncStructuredNode):
    """成果."""

    __label__ = "Archievement"
    total_char = IntegerProperty()
    total_sentence = IntegerProperty()
    n_resource = IntegerProperty()
    created = DateTimeNeo4jFormatProperty()

    user = AsyncRelationshipFrom(LUser, "ARCHEIVE", cardinality=AsyncZeroOrOne)
    prev = AsyncRelationshipTo(
        "LArchievement",
        "PREV",
        cardinality=AsyncZeroOrOne,
    )
