"""user repository."""
from __future__ import annotations

from neomodel import (
    BooleanProperty,
    DateTimeProperty,
    EmailProperty,
    IntegerProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
    ZeroOrOne,
)


class LUser(StructuredNode):
    """Neo4j label."""

    __label__ = "User"
    uid = UniqueIdProperty()
    email = EmailProperty()
    hashed_password = StringProperty()
    is_active = BooleanProperty(default=True)
    is_verified = BooleanProperty(default=False)
    is_superuser = BooleanProperty(default=False)
    created = DateTimeProperty(default_now=True)

    accounts = RelationshipTo("LAccount", "OAUTH")


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
