"""router param."""

from uuid import UUID

from pydantic import BaseModel, Field

from knowde.integration.user_achivement.domain import UserSearchOrderKey
from knowde.shared.cypher import Paging


class UserSearchBody(BaseModel, frozen=True):
    """ユーザー検索パラメータ."""

    q: str = ""
    paging: Paging = Field(default_factory=Paging)
    desc: bool = True
    order_by: list[UserSearchOrderKey] | None = None


class UserActivityRequest(BaseModel, frozen=True):  # noqa: D101
    user_ids: list[UUID | str]


class AchievementSnapshotResult(BaseModel, frozen=True):
    """成果スナップショット実行結果."""

    n_all_users: int
    n_target: int
    n_saved: int
