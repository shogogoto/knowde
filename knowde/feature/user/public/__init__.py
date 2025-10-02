"""認証なしで使える単純なuser検索.

entryやknowdeが絡むような機能はそっちのfeatureで書く
"""

from fastapi import APIRouter
from neomodel import Q

from knowde.feature.user.errors import UserNotFoundError
from knowde.feature.user.schema import UserReadPublic
from knowde.integration.user_achivement.router.router import user_achievement_router
from knowde.shared.user.label import LUser
from knowde.shared.user.router_util import TrackUser

_r = APIRouter(tags=["public_user"])


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


_r.include_router(user_achievement_router())


def public_user_router() -> APIRouter:  # noqa: D103
    return _r
