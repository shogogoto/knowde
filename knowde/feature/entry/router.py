"""routers."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends

from knowde.feature.entry import NameSpace
from knowde.feature.entry.category.folder.repo import fetch_namespace
from knowde.feature.entry.namespace import ResourceMetas, sync_namespace
from knowde.feature.user.domain import User
from knowde.shared.user.router_util import auth_component

router = APIRouter(tags=["entry"])


def entry_router() -> APIRouter:  # noqa: D103
    return router


@router.post("/namespace")
async def sync_paths(
    metas: ResourceMetas,
    user: Annotated[User, Depends(auth_component().current_user(active=True))],
) -> list[Path]:
    """ファイルシステムと同期."""
    ns = await fetch_namespace(user.id)
    return await sync_namespace(metas, ns)


@router.get("/namespace")
async def get_namaspace(
    user: Annotated[User, Depends(auth_component().current_user(active=True))],
) -> NameSpace:
    """ユーザーの名前空間."""
    return await fetch_namespace(user.id)
