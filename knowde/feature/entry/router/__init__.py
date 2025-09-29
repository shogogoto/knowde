"""routers."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import chardet  # 文字エンコーディング検出用
from fastapi import APIRouter, Body, Depends, UploadFile

from knowde.feature.entry.domain import NameSpace, ResourceDetail, ResourceSearchResult
from knowde.feature.entry.namespace import (
    ResourceMetas,
    fetch_info_by_resource_uid,
    fetch_namespace,
    sync_namespace,
)
from knowde.feature.entry.resource.repo.restore import restore_sysnet
from knowde.feature.entry.resource.repo.search import search_resources
from knowde.feature.entry.resource.usecase import save_resource_with_detail
from knowde.feature.entry.router.param import ResourceSearchBody
from knowde.feature.user.domain import User
from knowde.shared.user.router_util import TrackUser, auth_component

router = APIRouter(tags=["entry"])


def entry_router() -> APIRouter:  # noqa: D103
    return router


@router.post("/namespace")
async def sync_namespace_api(
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


async def read_content(file: UploadFile) -> str:
    """ファイルの内容を適切なエンコーディングで読み込む."""
    content = await file.read()
    encoding = chardet.detect(content)["encoding"] or "utf-8"
    return content.decode(encoding)


@router.post("/resource-text")
async def post_text(
    txt: Annotated[str, Body(embed=True)],
    path: Annotated[list[str], Body(embed=True)],
    user: Annotated[User, Depends(auth_component().current_user(active=True))],
) -> dict[str, str]:
    """テキストからsysnetを読み取って永続化."""
    ns = await fetch_namespace(user.id)
    m, _, _ = await save_resource_with_detail(ns, txt, path)
    return {"resource_id": m.uid.hex}


@router.post("/resource")
async def post_files(
    files: list[UploadFile],
    user: Annotated[User, Depends(auth_component().current_user(active=True))],
) -> None:
    """ファイルからsysnetを読み取って永続化."""
    for f in files:
        ns = await fetch_namespace(user.id)
        txt = await read_content(f)
        await save_resource_with_detail(ns, txt)


@router.get("/resource/{resource_id}")
async def get_resource_detail(resource_id: str) -> ResourceDetail:
    """リソース詳細."""
    sn, _ = await restore_sysnet(resource_id)
    info = await fetch_info_by_resource_uid(resource_id)
    return ResourceDetail(network=sn, resource_info=info)


@router.post("/resource/search")
async def search_resource_post(
    body: ResourceSearchBody,
    user: TrackUser = None,
) -> ResourceSearchResult:
    """リソース検索(POST)."""
    return await search_resources(
        search_str=body.q,
        paging=body.paging,
        search_user=body.q_user,
        desc=body.desc,
        keys=body.order_by,
    )
