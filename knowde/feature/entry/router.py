"""routers."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from knowde.feature.auth.routers import auth_component
from knowde.feature.entry import NameSpace
from knowde.feature.entry.category.folder.repo import fetch_namespace
from knowde.feature.entry.namespace import ResourceMetas, sync_namespace

if TYPE_CHECKING:
    from knowde.feature.user import User

router = APIRouter(tags=["entry"])


def entry_router() -> APIRouter:  # noqa: D103
    return router


@router.post("/namespace")
async def sync_paths(
    metas: ResourceMetas,
    user: User = Depends(auth_component().current_user(active=True)),  # noqa: FAST002
) -> list[Path]:
    """ファイルシステムと同期."""
    ns = fetch_namespace(user.id)
    return sync_namespace(metas, ns)


@router.get("/namespace")
async def get_namaspace(
    user: User = Depends(auth_component().current_user(active=True)),  # noqa: FAST002
) -> NameSpace:
    """ユーザーの名前空間."""
    return fetch_namespace(user.id)
