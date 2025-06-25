"""系の永続化 router."""

from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

import chardet  # 文字エンコーディング検出用
from fastapi import APIRouter, Depends, UploadFile

from knowde.complex.__core__.tree2net import parse2net
from knowde.complex.entry import ResourceMeta
from knowde.complex.entry.category.folder.repo import fetch_namespace
from knowde.complex.entry.label import LResource
from knowde.complex.nxdb.save import sn2db
from knowde.feature.auth.routers import auth_component

if TYPE_CHECKING:
    from knowde.primitive.user import User


@cache
def nxdb_router() -> APIRouter:  # noqa: D103 auto-import のために関数化
    return APIRouter()


async def read_content(file: UploadFile) -> str:
    """ファイルの内容を適切なエンコーディングで読み込む."""
    content = await file.read()
    encoding = chardet.detect(content)["encoding"] or "utf-8"
    return content.decode(encoding)


@nxdb_router().post("/upload")
async def read_file(
    files: list[UploadFile],
    user: User = Depends(auth_component().current_user(active=True)),
) -> None:
    """ファイルからsysnetを読み取って永続化."""
    ns = fetch_namespace(user.id)
    for f in files:
        txt = await read_content(f)
        sn = parse2net(txt)
        meta = ResourceMeta.of(sn)
        r = ns.get_resource_or_none(meta.title)
        if r is None:
            lb = LResource(**meta.model_dump()).save()
        else:
            lb = LResource(**r.model_dump())
            lb.refresh()
        sn2db(sn, lb.uid)
