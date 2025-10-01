"""repo."""

from datetime import datetime, timedelta
from typing import get_args
from uuid import UUID

from neomodel.async_.core import AsyncDatabase

from knowde.integration.user_archivement.cypher import q_archivement
from knowde.shared.cypher import Paging
from knowde.shared.user.schema import UserReadPublic
from knowde.shared.util import TZ

from .domain import (
    UserAchievement,
    UserSearchOrderKey,
    UserSearchResult,
    UserSearchRow,
)


async def fetch_user_with_current_achivement(
    search_str: str = "",
    paging: Paging = Paging(),
    keys: list[UserSearchOrderKey] | None = None,
    desc: bool = True,  # noqa: FBT001, FBT002
) -> UserSearchResult:
    """リアルタイムの成果でユーザー検索."""
    if keys is None:
        keys = ["username"]
    skeys = []
    for k in keys:
        if k in get_args(UserSearchOrderKey):
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
        {q_archivement("u")}
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
        archivement = UserAchievement(
            n_char=n_char,
            n_sentence=n_sentence,
            n_resource=n_resource,
        )
        data.append(UserSearchRow(user=user, archivement=archivement))
    return UserSearchResult(
        total=total,
        data=data,
    )


def week_start(now: datetime) -> str:
    """現在から6日前の日付を計算し、Cypherパラメータ用の文字列として返す."""
    week_start_dt = now - timedelta(days=6)
    return week_start_dt.isoformat()


# バッチ実行で使用
async def snapshot_archivement(
    now: datetime = datetime.now(tz=TZ),
    paging: Paging = Paging(size=10000),  # user数多すぎる場合の対応を想定
) -> tuple[int, int, int]:
    """成果を保存.

    最新のものをuserの近くに配置しPREVで古いものを辿れる
    今週の成果スナップショットが未作成のときに新規作成する
    今週とは、現在日から過去6日分のこと
    Returns:
        tuple[int, int, int]: 全user数、処理対象数、 スナップショット作成数
    """
    q = f"""
        MATCH (u: User)
        WITH COLLECT(u) AS all_users
        WITH all_users[$offset..$offset + $limit] AS users_in_page
            , SIZE(all_users) AS n_all_users
        WITH users_in_page, n_all_users
            , SIZE(users_in_page) AS n_target
        UNWIND CASE
            WHEN n_target = 0 THEN [NULL]
            ELSE users_in_page
        END AS u
        OPTIONAL MATCH (u)-[r_latest:ARCHEIVE]->(latest:Archievement)
        WITH u, r_latest, latest
            , CASE
                WHEN latest IS NULL THEN true
                WHEN latest.created < datetime($week_start) THEN true
                ELSE false
              END AS should_create
            , n_all_users
            , n_target

        CALL (u, r_latest, latest, should_create) {{
            WITH u, r_latest, latest, should_create
                , datetime() AS now
            WHERE should_create
                AND u IS NOT NULL
            {q_archivement("u")}
                , r_latest, latest
                , now, should_create

            FOREACH(i IN CASE WHEN r_latest IS NOT NULL THEN [1] ELSE [] END |
                DELETE r_latest
            )
            CREATE (u)-[:ARCHEIVE]->(newA:Archievement {{
                n_char: COALESCE(n_char, 0)
                , n_sentence: COALESCE(n_sentence, 0)
                , n_resource: COALESCE(n_resource, 0)
                , created: now
            }})
            FOREACH(i IN CASE WHEN latest IS NOT NULL THEN [1] ELSE [] END |
                CREATE (newA)-[:PREV]->(latest)
            )
            RETURN COUNT(u) AS total_created
        }} IN TRANSACTIONS OF 1 ROW // Neo4j 5.0 以降の並列化オプション
        RETURN n_all_users
            , n_target
            , SUM(total_created) AS n_processed
    """

    rows, _ = await AsyncDatabase().cypher_query(
        q,
        params={
            "offset": paging.skip,
            "limit": paging.size,
            "week_start": week_start(now),
        },
    )
    return tuple(rows[0])  # total,


async def fetch_activity(user_id: UUID) -> None:
    """直近成果の活動を取得."""
