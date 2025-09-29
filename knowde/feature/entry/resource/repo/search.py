"""リソース検索."""

from typing import get_args

from fastapi import status
from neomodel.async_.core import AsyncDatabase

from knowde.feature.entry.domain import (
    ResourceOrderKey,
    ResourceSearchResult,
    StatsOrderKey,
    UserOrderKey,
)
from knowde.feature.entry.mapper import MResource
from knowde.feature.entry.resource.stats.domain import ResourceStats
from knowde.feature.knowde import ResourceInfo
from knowde.feature.knowde.repo.clause import Paging
from knowde.shared.errors import DomainError
from knowde.shared.user.schema import UserReadPublic


async def search_total_resources(search_str: str, search_user: str) -> int:
    """検索にマッチするリソース総数."""
    q = """
        MATCH (r:Resource
            WHERE r.title CONTAINS $s
                //OR ANY(author IN r.authors WHERE author CONTAINS $s)
            )
            , (u:User)<-[:OWNED|PARENT]-*(r)
        WHERE u.username CONTAINS $u OR u.display_name CONTAINS $u
        RETURN COUNT(r)
    """
    rows, _ = await AsyncDatabase().cypher_query(
        q,
        params={"s": search_str, "u": search_user},
    )
    try:
        return rows[0][0]
    except IndexError as e:
        msg = "Failed to get total count from query result."
        raise DomainError(msg=msg, status_code=status.HTTP_502_BAD_GATEWAY) from e


async def search_resources(  # noqa: PLR0917
    search_str: str,
    paging: Paging = Paging(),
    search_user: str = "",  # username or display name
    keys: list[ResourceOrderKey | StatsOrderKey | UserOrderKey] | None = None,
    desc: bool = True,  # noqa: FBT001, FBT002
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> ResourceSearchResult:
    """リソース検索."""
    if keys is None:
        keys = ["username"]
    skeys = []
    for k in keys:
        if k in get_args(ResourceOrderKey):
            q_ord = f"r.{k}"
        elif k in get_args(StatsOrderKey):
            q_ord = f"stat.{k}"
        elif k in get_args(UserOrderKey):
            q_ord = f"u.{k}"
        else:
            msg = f"Unknown order key: {k}"
            raise TypeError(msg)
        skeys.append(q_ord)
    q = f"""
        MATCH (r:Resource WHERE r.title CONTAINS $s
                //OR ANY(author IN r.authors WHERE author CONTAINS $s)
            )
            -[:STATS]->(stat:ResourceStatsCache)
            , (u:User)<-[:OWNED|PARENT]-*(r)
        WHERE u.username CONTAINS $u OR u.display_name CONTAINS $u
        ORDER BY {", ".join(skeys)} {((desc and "DESC") or "ASC")}
        {paging.phrase()}
        RETURN r, stat, u
    """
    if do_print:
        print(q)  # noqa: T201
    rows, _ = await AsyncDatabase().cypher_query(
        q,
        params={"s": search_str, "u": search_user},
    )
    infos = []
    for row in rows:
        r, stat, u = row
        info = ResourceInfo(
            user=UserReadPublic.model_validate(u),
            resource=MResource.freeze_dict(r),
            resource_stats=ResourceStats.model_validate(stat),
        )
        infos.append(info)

    return ResourceSearchResult(
        total=await search_total_resources(search_str, search_user),
        data=infos,
    )
