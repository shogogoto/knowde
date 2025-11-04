"""router."""

from typing import Annotated

from fastapi import APIRouter, Query

from knowde.integration.user_achivement.domain import (
    AchievementHistories,
    UserSearchResult,
    UserSearchRow,
)
from knowde.integration.user_achivement.repo import (
    fetch_achievement_history,
    fetch_activity,
    fetch_user_with_current_achivement,
    snapshot_archivement,
)
from knowde.shared.cypher import Paging
from knowde.shared.user.router_util import TrackUser

from .param import (
    AchievementSnapshotResult,
    UserActivityRequest,
    UserSearchBody,
)

_r = APIRouter()


@_r.post("/search")
async def search_user(
    body: UserSearchBody,
    user: TrackUser = None,
) -> UserSearchResult:
    """認証なしユーザー検索."""
    return await fetch_user_with_current_achivement(
        search_str=body.q,
        paging=body.paging,
        keys=body.order_by,
        desc=body.desc,
    )


@_r.post("/activity")
async def get_user_activity(
    req: UserActivityRequest,
) -> list[UserSearchRow]:
    """複数ユーザーの現在の成果をまとめて取得."""
    return await fetch_activity(req.user_ids)


# TODO: API Keyを渡すのは急ぎではないがいつかやる  # noqa: FIX002, TD002, TD003
@_r.post(
    "/achievement/batch",
    # dependencies=[Depends(get_api_key)]
)
async def save_user_achievement(
    page: Annotated[int, Query(gt=0)] = 1,
    size: Annotated[int, Query(gt=0)] = 10000,
) -> AchievementSnapshotResult:
    """バッチ処理などで利用する成果の保存API."""
    n_all_users, n_target, n_saved = await snapshot_archivement(
        paging=Paging(page=page, size=size),
    )
    return AchievementSnapshotResult(
        n_all_users=n_all_users,
        n_target=n_target,
        n_saved=n_saved,
    )


@_r.post("/archievement-history")
async def get_archievement_history(
    req: UserActivityRequest,
) -> AchievementHistories:
    """指定ユーザーの週間成果履歴."""
    return await fetch_achievement_history(req.user_ids)


def user_achievement_router() -> APIRouter:  # noqa: D103
    return _r
