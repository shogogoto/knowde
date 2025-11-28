"""usecase."""

from datetime import datetime

from neomodel.async_.core import AsyncDatabase

from knowde.feature.entry.domain import NameSpace, ResourceMeta
from knowde.feature.entry.errors import ResourceSaveOptimisticLockError
from knowde.feature.entry.label import LResource
from knowde.feature.entry.mapper import MResource
from knowde.feature.entry.namespace import (
    fetch_namespace,
    save_or_move_resource,
)
from knowde.feature.entry.resource.repo.diff_update.repo import update_resource_diff
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
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> tuple[MResource, ResourceMeta, SysNet]:
    """テキストからResource内のKnowdeネットワークを永続化.

    ファイルアップロードを繰り返したときにリソースが重複で作成されてしまった
    これを解決するために楽観的ロックを導入しようとしている

    テストパターン
        新規同時
        更新同時
    """
    meta, sn = ResourceMeta.from_str(txt)
    if path is not None:
        meta.path = tuple(path)
    if updated is not None:
        meta.updated = updated
    # Writeを伴うものはすべてtransactionに含める
    async with AsyncDatabase().transaction:
        # 新規, 新規で同時に処理が来た場合に
        lb = await save_or_move_resource(meta, ns)
        rs = await LResource.nodes.filter(title=meta.title, txt_hash=meta.txt_hash)
        if len(rs) > 1:
            msg = "同一リソースを重複して新規作成しました"
            raise ResourceSaveOptimisticLockError(msg)

        if lb is None:
            msg = f"{meta.title} の保存に失敗しました"
            raise NotFoundError(msg)
        old = MResource.freeze_dict(lb.__properties__)
        cache = await lb.cached_stats.get_or_none()
        await save_resource_stats_cache(old.uid, sn)
        already = ns.get_resource_or_none(meta.title)
        if cache is None or already is None:  # 新規作成
            await sn2db(sn, lb.uid, do_print)
        is_changed = already is not None and already.txt_hash != old.txt_hash
        if is_changed:
            await update_resource_diff(lb.uid, sn)
        # 適切な status code と message を与える
        # cache_for_lock_check = await lb.cached_stats.get_or_none()

        return old, meta, sn


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
