"""repo."""

from typing import get_args

from neomodel.async_.core import AsyncDatabase

from knowde.integration.user_score.domain import (
    UserAcheivement,
    UserScoreOrderKey,
    UserSearchResult,
    UserSearchRow,
)
from knowde.shared.cypher import Paging
from knowde.shared.user.schema import UserReadPublic


async def fetch_user_with_achivement(
    search_str: str = "",
    paging: Paging = Paging(),
    keys: list[UserScoreOrderKey] | None = None,
    desc: bool = True,  # noqa: FBT001, FBT002
) -> UserSearchResult:
    """成果付きでユーザー検索."""
    if keys is None:
        keys = ["username"]
    skeys = []
    for k in keys:
        if k in get_args(UserScoreOrderKey):
            if k in {"username", "display_name"}:
                skeys.append(f"u.{k}")
            else:
                skeys.append(k)
        else:
            msg = f"Unknown order key: {k}"
            raise TypeError(msg)

    q = f"""
        MATCH (u:User)
        WHERE u.username CONTAINS $s
            OR u.display_name CONTAINS $s
        OPTIONAL MATCH (u)<-[:OWNED|PARENT]-*(r:Resource)
            -[:STATS]->(stat:ResourceStatsCache)
        WITH u
            , SUM(stat.n_char) AS n_char
            , SUM(stat.n_sentence) AS n_sentence
            , COUNT(r) AS n_resource

        ORDER BY {", ".join(skeys)} {((desc and "DESC") or "ASC")}

        WITH COLLECT({{
            u:u
            , n_char:n_char
            , n_sentence:n_sentence
            , n_resource:n_resource
        }}) AS results
        RETURN SIZE(results) AS total
            , results[$offset..$offset + $limit] AS page
    """
    rows, _ = await AsyncDatabase().cypher_query(
        q,
        params={
            "s": search_str,
            "offset": paging.skip,
            "limit": paging.size,
        },
    )
    data = []
    if not rows:
        return UserSearchResult(total=0, data=data)
    total, page = rows[0]
    for row in page:
        u, n_char, n_sentence, n_resource = (
            row["u"],
            row["n_char"],
            row["n_sentence"],
            row["n_resource"],
        )
        user = UserReadPublic.model_validate(u)
        archivement = UserAcheivement(
            n_char=n_char,
            n_sentence=n_sentence,
            n_resource=n_resource,
        )
        data.append(UserSearchRow(user=user, archivement=archivement))
    return UserSearchResult(
        total=total,
        data=data,
    )
