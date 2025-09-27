"""リソース検索."""

from fastapi import status
from neomodel.async_.core import AsyncDatabase

from knowde.feature.entry.domain import ResourceSearchResult
from knowde.feature.entry.mapper import MResource
from knowde.feature.entry.resource.stats.domain import ResourceStats
from knowde.feature.knowde import ResourceInfo
from knowde.feature.knowde.repo.clause import Paging
from knowde.shared.errors import DomainError
from knowde.shared.user.schema import UserReadPublic

# - [ ] リソース検索API作成
#   - [ ] メタ情報含め
#   - [ ] 名前で
#   - [ ] usernameで
#   - [ ] リソース統計値をDBに登録・更新できるようにする
#     いちいちnode数を数えるのは負荷高すぎ
#   - [ ] 統計値ソート
#   - [ ] publishedソート
#   - [ ] 作成日ソート


async def search_total_resources(search_str: str, search_user: str) -> int:
    """検索にマッチするリソース総数."""
    q = """
        MATCH (r:Resource WHERE r.title CONTAINS $s)
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


async def search_resources(
    search_str: str,
    paging: Paging = Paging(),
    search_user: str = "",  # username or display name
) -> ResourceSearchResult:
    """リソース検索."""
    q = f"""
        MATCH (r:Resource WHERE r.title CONTAINS $s)
            -[:STATS]->(stat:ResourceStatsCache)
            , (u:User)<-[:OWNED|PARENT]-*(r)
        WHERE u.username CONTAINS $u OR u.display_name CONTAINS $u
        {paging.phrase()}
        RETURN r, stat, u
    """
    #     q_where = q_where_resource(key, where)
    #     q = f"""
    #         CALL () {{
    #             {q_where}
    #         }}
    #         WITH r
    #         {(order_by.phrase() if order_by else "")}
    #         {paging.phrase()}
    #         RETURN r.uid
    #     """
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
