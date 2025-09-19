"""リソース統計情報のneo4j label."""

from knowde.feature.entry.label import LResource, LResourceStatsCache
from knowde.feature.parsing.sysnet import SysNet
from knowde.shared.types import UUIDy, to_uuid

from .domain import (
    ResourceStatsCohesion,
    ResourceStatsHeavy,
    ResourceStatsRichness,
)


async def save_resource_stats_cache(
    resource_uid: UUIDy,
    sn: SysNet,
) -> LResourceStatsCache:
    """統計値を保存."""
    r: LResource = await LResource.nodes.get(uid=to_uuid(resource_uid).hex)
    s: LResourceStatsCache | None = await r.cached_stats.get_or_none()

    retval = ResourceStatsCohesion.create(sn).model_dump()
    retval.update(ResourceStatsRichness.create(sn).model_dump())
    retval.update(ResourceStatsHeavy.create(sn).model_dump())

    if s is not None:
        for k, v in retval.items():
            setattr(s, k, v)
        return await s.save()
    lb = await LResourceStatsCache(**retval).save()
    await r.cached_stats.connect(lb)
    return lb


async def fetch_resource_stats_cache(resource_uid: UUIDy) -> LResourceStatsCache | None:
    """統計値を取得."""
    r: LResource = await LResource.nodes.get(uid=to_uuid(resource_uid).hex)
    return await r.cached_stats.get_or_none()
