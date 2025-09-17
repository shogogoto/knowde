"""usecase."""

from __future__ import annotations

from knowde.feature.entry.namespace.stats.domain import (
    ResourceStatsHeavy,
    ResourceStatsStd,
)
from knowde.feature.parsing.domain import try_parse2net


def to_resource_stats(
    txt: str,
    heavy: bool,  # noqa: FBT001
) -> dict[str, int | float | str]:
    """統計値."""
    sn = try_parse2net(txt)
    retval = ResourceStatsStd.create(sn).model_dump()
    if heavy:
        retval.update(ResourceStatsHeavy.create(sn).model_dump())
    return retval
