"""usecase."""

from datetime import datetime
from uuid import UUID

from knowde.feature.entry.domain import NameSpace, ResourceMeta
from knowde.feature.entry.errors import ResourceSaveOptimisticLockError
from knowde.feature.entry.label import LResource
from knowde.feature.entry.mapper import MResource
from knowde.feature.entry.namespace import (
    fetch_namespace,
    fetch_resources_by_user,
    save_or_move_resource,
)
from knowde.feature.entry.resource.repo.diff_update.repo import update_resource_diff
from knowde.feature.entry.resource.repo.save import sn2db
from knowde.feature.parsing.sysnet import SysNet
from knowde.shared.errors.domain import NotFoundError
from knowde.shared.types import UUIDy, to_uuid

from .stats.repo import save_resource_stats_cache


async def _check_duplication(user_id: UUID, title: str):
    rs = await fetch_resources_by_user(user_id)
    rs = [r for r in rs if r.name == title]
    if len(rs) > 1:
        msg = f"同一リソース'{title}を重複して新規作成しました"
        raise ResourceSaveOptimisticLockError(msg)


async def save_resource_with_detail(
    ns: NameSpace,
    txt: str,
    path: list[str] | None = None,
    updated: datetime | None = None,
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> tuple[MResource, ResourceMeta, SysNet]:
    """テキストからResource内のKnowdeネットワークを永続化."""
    meta, sn = ResourceMeta.from_str(txt)
    if path is not None:
        meta.path = tuple(path)
    if updated is not None:
        meta.updated = updated
    lb = await save_or_move_resource(meta, ns)
    await _check_duplication(ns.user_id, meta.title)
    r = await LResource.nodes.get(uid=lb.uid)
    if updated is not None and r.updated != updated:
        msg = f"'{meta.title}'は同時に更新されたのでロールバック"
        raise ResourceSaveOptimisticLockError(msg)

    if lb is None:
        msg = f"{meta.title} の保存に失敗しました"
        raise NotFoundError(msg)
    dbmeta = MResource.freeze_dict(lb.__properties__)
    cache = await lb.cached_stats.get_or_none()
    await save_resource_stats_cache(dbmeta.uid, sn)

    if cache is None:  # 新規作成
        await sn2db(sn, lb.uid, do_print)
    if cache is not None and meta.txt_hash != dbmeta.txt_hash:  # 差分更新
        await update_resource_diff(lb.uid, sn)

    return dbmeta, meta, sn


async def save_text(
    user_id: UUIDy,
    s: str,
    path: tuple[str, ...] | None = None,
    updated: datetime | None = None,
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> tuple[SysNet, MResource]:
    """テキストをリソース詳細として保存するラッパー."""
    ns = await fetch_namespace(to_uuid(user_id))
    m, _meta, sn = await save_resource_with_detail(
        ns,
        s,
        list(path) if path is not None else None,
        updated,
        do_print,
    )
    return sn, m
