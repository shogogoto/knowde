"""user repository."""

from __future__ import annotations

from neomodel import (
    AsyncRelationshipFrom,
    AsyncStructuredNode,
    AsyncZeroOrOne,
    EmailProperty,
    IntegerProperty,
    StringProperty,
)

from knowde.shared.user.label import LUser


class LAccount(AsyncStructuredNode):
    """for fastapi-users Single Sign On."""

    __label__ = "Account"
    oauth_name = StringProperty()
    access_token = StringProperty()
    expires_at = IntegerProperty()
    refresh_token = StringProperty()
    account_id = StringProperty()
    account_email = EmailProperty()

    user = AsyncRelationshipFrom(LUser, "OAUTH", cardinality=AsyncZeroOrOne)
