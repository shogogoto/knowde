"""user repository."""
from __future__ import annotations

from neomodel import (
    BooleanProperty,
    DateTimeProperty,
    EmailProperty,
    IntegerProperty,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
)


class LAccount(StructuredNode):
    """Neo4j label."""

    __label__ = "Account"
    uid = UniqueIdProperty()
    email = EmailProperty()
    hashed_password = StringProperty()
    is_active = BooleanProperty(default=True)
    is_verified = BooleanProperty()
    is_superuser = BooleanProperty()
    created = DateTimeProperty(default_now=True)


class LSSOAccount(StructuredNode):
    """Neo4j label."""

    __label__ = "SSOAccount"
    uid = UniqueIdProperty()
    oauth_name = StringProperty()
    access_token = StringProperty()
    expires_at = IntegerProperty()
    refresh_token = StringProperty()
    account_id = StringProperty()
    account_email = EmailProperty()
