"""shared user label."""

from __future__ import annotations

from typing import Any, override

from neomodel import (
    AsyncStructuredNode,
    BooleanProperty,
    DateTimeNeo4jFormatProperty,
    EmailProperty,
    RelationshipTo,
    StringProperty,
    UniqueIdProperty,
)

from knowde.feature.user import LEN_DISPLAY_NAME, LEN_PROFILE
from knowde.feature.user.repo.label import LAccount


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
    username = StringProperty(default=None, pattern=r"^[^-]*$")
    # oauth
    accounts = RelationshipTo(LAccount, "OAUTH")
