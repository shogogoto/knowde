"""usecase."""

from datetime import datetime

from neomodel import adb

from knowde.feature.entry.domain import NameSpace, ResourceMeta
from knowde.feature.entry.mapper import MResource
from knowde.feature.entry.namespace import (
    fetch_namespace,
    save_or_move_resource,
)
from knowde.feature.entry.resource.repo.save import sn2db
from knowde.feature.parsing.sysnet import SysNet
from knowde.shared.errors.domain import NotFoundError
from knowde.shared.types import UUIDy, to_uuid

from .stats.repo import save_resource_stats_cache


async def save_resource_with_detail(
    ns: NameSpace,
    txt: str,
    path: list[str] | None = None,
    updated: datetime | None = None,
) -> tuple[MResource, ResourceMeta, SysNet]:
    """テキストからResource内のKnowdeネットワークを永続化."""
    meta, sn = ResourceMeta.from_str(txt)
    if path is not None:
        meta.path = tuple(path)
    if updated is not None:
        meta.updated = updated

    now = ns.get_resource_or_none(meta.title)

    async with adb.transaction:
        lb = await save_or_move_resource(meta, ns)
        if lb is None:
            msg = f"{meta.title} の保存に失敗しました"
            raise NotFoundError(msg)
        old = MResource.freeze_dict(lb.__properties__)
        cache = await lb.cached_stats.get_or_none()
        await save_resource_stats_cache(old.uid, sn)
        # 未キャッシュ=新規登録 or hash更新時
        is_changed = cache is None or now is None or now.txt_hash != old.txt_hash
        if is_changed:
            await sn2db(sn, lb.uid)  # ここで freezeする
        return old, meta, sn


async def save_text(
    user_id: UUIDy,
    s: str,
    path: tuple[str, ...] | None = None,
    updated: datetime | None = None,
) -> tuple[SysNet, MResource]:
    """テキストをリソース詳細として保存するラッパー."""
    ns = await fetch_namespace(to_uuid(user_id))
    m, _meta, sn = await save_resource_with_detail(
        ns,
        s,
        list(path) if path is not None else None,
        updated,
    )
    return sn, m
