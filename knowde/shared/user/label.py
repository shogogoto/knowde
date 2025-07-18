"""shared user label."""

from __future__ import annotations

from typing import Any, override

from neomodel import (
    AsyncRelationshipFrom,
    AsyncRelationshipManager,
    AsyncRelationshipTo,
    AsyncStructuredNode,
    AsyncZeroOrOne,
    BooleanProperty,
    DateTimeNeo4jFormatProperty,
    EmailProperty,
    IntegerProperty,
    StringProperty,
    UniqueIdProperty,
)

from . import LEN_DISPLAY_NAME, LEN_PROFILE, MAX_LEN_USERNAME


# cyclic import を避けるためにここに置かざるを得ず
class LAccount(AsyncStructuredNode):
    """for fastapi-users Single Sign On."""

    __label__ = "Account"
    oauth_name = StringProperty()
    access_token = StringProperty()
    expires_at = IntegerProperty()
    refresh_token = StringProperty()
    account_id = StringProperty()
    account_email = EmailProperty()

    user: AsyncRelationshipManager = AsyncRelationshipFrom(
        "LUser",
        "OAUTH",
        cardinality=AsyncZeroOrOne,
    )


class LowerEmailProperty(EmailProperty):  # noqa: D101
    @override
    def normalize(self, value: Any) -> str:
        val = super().normalize(value)
        return val.lower()


class LUser(AsyncStructuredNode):
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
    profile = StringProperty(default=None, max_length=LEN_PROFILE)
    avatar_url = StringProperty(default=None)
    username = StringProperty(
        default=None,
        pattern=r"^[^-]*$",
        unique_index=True,
        max_lenght=MAX_LEN_USERNAME,
    )
    accounts: AsyncRelationshipManager = AsyncRelationshipTo(LAccount, "OAUTH")
