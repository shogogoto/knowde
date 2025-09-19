"""usecase."""

from __future__ import annotations

from knowde.feature.parsing.domain import try_parse2net

from .domain import (
    ResourceStats,
    ResourceStatsCohesion,
    ResourceStatsHeavy,
    ResourceStatsRichness,
)


def to_resource_stats(
    txt: str,
    heavy: bool,  # noqa: FBT001
) -> ResourceStats:
    """統計値."""
    sn = try_parse2net(txt)
    retval = ResourceStatsCohesion.create(sn).model_dump()
    retval.update(ResourceStatsRichness.create(sn).model_dump())
    if heavy:
        retval.update(ResourceStatsHeavy.create(sn).model_dump())

    return ResourceStats.model_validate(retval)
