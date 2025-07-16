"""認証なしで使える単純なuser検索.

entryやknowdeが絡むような機能はそっちのfeatureで書く
"""

from typing import Annotated

from fastapi import APIRouter, Query
from neomodel import Q

from knowde.feature.user.schema import UserReadPublic
from knowde.shared.user.label import LUser
from knowde.shared.user.router_util import TrackUser

_r = APIRouter(tags=["public_user"])


@_r.get("/search")
async def search_user(
    display_name: Annotated[str, Query()] = "",
    id: Annotated[str, Query()] = "",  # noqa: A002
    user: TrackUser = None,
) -> list[UserReadPublic]:
    """認証なしユーザー検索."""
    q = Q()
    if id:
        q |= Q(uid__istartswith=id.replace("-", "")) | Q(username__icontains=id)

    if display_name:
        q &= Q(display_name__icontains=display_name)

    users = await LUser.nodes.filter(q).order_by("display_name", "username", "uid")
    return [UserReadPublic.model_validate(u.__properties__) for u in users]


@_r.get("/profile/{username}")
async def get_profile(
    username: Annotated[str, Query()] = "",
    user: TrackUser = None,
) -> UserReadPublic:
    """公開ユーザー情報."""
    q = Q()
    if id:
        q |= Q(uid__istartswith=id.replace("-", "")) | Q(username__icontains=id)


def public_user_router() -> APIRouter:  # noqa: D103
    return _r
