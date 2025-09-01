"""routers."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import chardet  # 文字エンコーディング検出用
from fastapi import APIRouter, Depends, UploadFile

from knowde.feature.entry import NameSpace, ResourceMeta
from knowde.feature.entry.category.folder.repo import fetch_namespace
from knowde.feature.entry.label import LResource
from knowde.feature.entry.namespace import ResourceMetas, sync_namespace
from knowde.feature.entry.resource.repo.save import sn2db
from knowde.feature.parsing.tree2net import parse2net
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


async def read_content(file: UploadFile) -> str:
    """ファイルの内容を適切なエンコーディングで読み込む."""
    content = await file.read()
    encoding = chardet.detect(content)["encoding"] or "utf-8"
    return content.decode(encoding)


@router.post("/upload")
async def read_file(
    files: list[UploadFile],
    user: Annotated[User, Depends(auth_component().current_user(active=True))],
) -> None:
    """ファイルからsysnetを読み取って永続化."""
    ns = await fetch_namespace(user.id)
    for f in files:
        txt = await read_content(f)
        sn = parse2net(txt)
        meta = ResourceMeta.of(sn)
        r = ns.get_resource_or_none(meta.title)
        if r is None:
            lb = await LResource(**meta.model_dump()).save()
        else:
            lb = LResource(**r.model_dump())
            await lb.refresh()
        sn2db(sn, lb.uid)


@router.get("/resource/{resource_id}")
async def get_resource_detail(
    resource_id: str,
    user: Annotated[User, Depends(auth_component().current_user(active=True))],
) -> None:
    """リソース詳細.

    aaaa
    ディレクトリ構成を整備
        file
            -> resource meta
            -> header
        parsing
        sentnet





    """
