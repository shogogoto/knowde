"""user repository."""

from __future__ import annotations

from neomodel import (
    EmailProperty,
    IntegerProperty,
    RelationshipFrom,
    StringProperty,
    StructuredNode,
    ZeroOrOne,
)


class LAccount(StructuredNode):
    """Neo4j label."""

    __label__ = "Account"
    oauth_name = StringProperty()
    access_token = StringProperty()
    expires_at = IntegerProperty()
    refresh_token = StringProperty()
    account_id = StringProperty()
    account_email = EmailProperty()

    user = RelationshipFrom("LUser", "OAUTH", cardinality=ZeroOrOne)
