"""認証なしで使える単純なuser検索.

entryやknowdeが絡むような機能はそっちのfeatureで書く
"""

from typing import Annotated

from fastapi import APIRouter, Query

from knowde.feature.user.schema import UserRead
from knowde.shared.labels.user import LUser

_r = APIRouter()


@_r.get("/search")
def search_user(
    name: Annotated[str | None, Query()] = "",
    id: Annotated[str | None, Query()] = "",  # noqa: A002
) -> list[UserRead]:
    """認証なしユーザー検索."""
    users = LUser.nodes.filter(
        display_name__icontains=name,
        uid__istartswith=id.replace("-", "") if id else "",
    ).order_by("display_name", "uid")
    return [UserRead.from_label(u) for u in users]


def authless_user_router() -> APIRouter:  # noqa: D103
    return _r
