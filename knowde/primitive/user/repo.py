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

from knowde.primitive.__core__.neoutil import auto_label


@auto_label
class LUser(StructuredNode):
    """Neo4j label."""

    uid = UniqueIdProperty()
    email = EmailProperty()
    hashed_password = StringProperty()
    is_active = BooleanProperty(default=True)
    is_verified = BooleanProperty(default=False)
    is_superuser = BooleanProperty(default=False)
    created = DateTimeProperty(default_now=True)

    accounts = RelationshipTo("LAccount", "OAUTH")


@auto_label
class LAccount(StructuredNode):
    """Neo4j label."""

    oauth_name = StringProperty()
    access_token = StringProperty()
    expires_at = IntegerProperty()
    refresh_token = StringProperty()
    account_id = StringProperty()
    account_email = EmailProperty()

    user = RelationshipFrom("LUser", "OAUTH", cardinality=ZeroOrOne)
