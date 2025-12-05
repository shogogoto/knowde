"""リソース統計情報のneo4j label."""

from knowde.feature.entry.label import LResource, LResourceStatsCache
from knowde.feature.parsing.sysnet import SysNet
from knowde.shared.types import UUIDy, to_uuid

from .domain import (
    create_resource_stats,
)


async def save_resource_stats_cache(
    resource_uid: UUIDy,
    sn: SysNet,
) -> LResourceStatsCache:
    """統計値を保存."""
    r: LResource = await LResource.nodes.get(uid=to_uuid(resource_uid).hex)
    s = await r.cached_stats.get_or_none()

    stats = create_resource_stats(sn)

    if s is not None and isinstance(s, LResourceStatsCache):
        for k, v in stats.items():
            setattr(s, k, v)
        return await s.save()
    lb = await LResourceStatsCache(**stats).save()
    await r.cached_stats.connect(lb)
    return lb


async def fetch_resource_stats_cache(resource_uid: UUIDy) -> LResourceStatsCache | None:
    """統計値を取得."""
    r: LResource = await LResource.nodes.get(uid=to_uuid(resource_uid).hex)
    return await r.cached_stats.get_or_none()
