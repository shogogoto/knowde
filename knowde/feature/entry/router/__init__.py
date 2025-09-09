"""routers."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import chardet  # 文字エンコーディング検出用
from fastapi import APIRouter, Body, Depends, UploadFile

from knowde.feature.entry import NameSpace, ResourceDetail
from knowde.feature.entry.namespace import (
    ResourceMetas,
    fetch_namespace,
    sync_namespace,
    text2resource,
)
from knowde.feature.entry.resource.repo.restore import restore_sysnet
from knowde.feature.user.domain import User
from knowde.shared.user.router_util import auth_component

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
    uid = await text2resource(ns, txt)
    return {"resource_id": uid}


@router.post("/resource")
async def post_files(
    files: list[UploadFile],
    user: Annotated[User, Depends(auth_component().current_user(active=True))],
) -> None:
    """ファイルからsysnetを読み取って永続化."""
    for f in files:
        ns = await fetch_namespace(user.id)
        txt = await read_content(f)
        await text2resource(ns, txt)


@router.get("/resource/{resource_id}")
async def get_resource_detail(
    resource_id: str,
    user: Annotated[User, Depends(auth_component().current_user(active=True))],
) -> ResourceDetail:
    """リソース詳細."""
    sn, _ = await restore_sysnet(resource_id)

    return ResourceDetail(network=sn)
