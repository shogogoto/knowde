"""user repository."""

from __future__ import annotations

from typing import Any, override

from neomodel import (
    BooleanProperty,
    DateTimeNeo4jFormatProperty,
    EmailProperty,
    IntegerProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    UniqueIdProperty,
    ZeroOrOne,
)

from knowde.feature.user.schema import LEN_DISPLAY_NAME


class LowerEmailProperty(EmailProperty):  # noqa: D101
    @override
    def normalize(self, value: Any) -> str:
        val = super().normalize(value)
        return val.lower()


class LUser(StructuredNode):
    """Neo4j label."""

    __label__ = "User"
    # 基本属性
    uid = UniqueIdProperty()
    email = LowerEmailProperty(unique_index=True)
    hashed_password = StringProperty(default=None)
    is_active = BooleanProperty(default=True)
    is_verified = BooleanProperty(default=False)
    is_superuser = BooleanProperty(default=False)
    created = DateTimeNeo4jFormatProperty(default_now=True)

    # 追加情報
    display_name = StringProperty(default=None, max_length=LEN_DISPLAY_NAME)
    profile = StringProperty(default=None)
    avatar_url = StringProperty(default=None)

    # oauth
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
