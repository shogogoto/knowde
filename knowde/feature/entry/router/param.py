"""API params."""

from fastapi import Query
from pydantic import BaseModel, Field

from knowde.feature.entry.domain import (
    ResourceOrderKey,
    StatsOrderKey,
    UserOrderKey,
)
from knowde.feature.knowde.repo.clause import Paging


class ResourceSearchBody(BaseModel, frozen=True):
    """リソース検索のPOST Body."""

    q: str = ""
    q_user: str = ""
    paging: Paging = Field(default_factory=Paging)
    desc: bool = True
    order_by: list[ResourceOrderKey | StatsOrderKey | UserOrderKey] | None = None


class ResourceSearchParams(BaseModel, frozen=True):
    """検索方法の指定."""

    q: str = Query("", title="title検索文字列")
    q_user: str = Query(
        "",
        title="user名検索文字列",
        description="username or display_nameでマッチするリソースを検索する",
    )
    paging: Paging = Field(default_factory=Paging)
    desc: bool = Query(default=True, description="降順")


def get_search_resource_param(
    q: str = Query("", description="title検索文字列"),
    q_user: str = Query(
        "",
        title="user名検索文字列",
        description="username or display_nameでマッチするリソースを検索する",
    ),
    page: int = Query(default=1, gt=0),
    size: int = Query(default=100, gt=0),
    desc: bool = Query(default=True, description="降順"),  # noqa: FBT001
) -> ResourceSearchParams:
    """検索方法の指定."""
    paging = Paging(page=page, size=size)
    return ResourceSearchParams(q=q, q_user=q_user, paging=paging, desc=desc)
