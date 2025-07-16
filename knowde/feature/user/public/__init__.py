"""認証なしで使える単純なuser検索.

entryやknowdeが絡むような機能はそっちのfeatureで書く
"""

from typing import Annotated

from fastapi import APIRouter, Query
from neomodel import Q

from knowde.feature.user.errors import UserNotFoundError
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
async def user_profile(username: str, user: TrackUser = None) -> UserReadPublic:
    """公開ユーザー情報."""
    q = Q(uid=username.replace("-", "")) | Q(username=username)
    lbs = await LUser.nodes.filter(q)
    if len(lbs) == 0:
        msg = f"user not found, {username}"
        raise UserNotFoundError(msg)
    if len(lbs) > 1:
        msg = f"user not unique, {username}"
        raise UserNotFoundError(msg)
    lb = lbs[0]
    return UserReadPublic.model_validate(lb.__properties__)


def public_user_router() -> APIRouter:  # noqa: D103
    return _r
