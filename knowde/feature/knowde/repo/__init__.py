"""repo."""

from textwrap import indent
from uuid import UUID

from fastapi import status
from more_itertools import collapse
from neomodel import adb, db

from knowde.feature.entry.namespace import resource_infos_by_resource_uids
from knowde.feature.knowde import (
    KAdjacency,
    Knowde,
    KnowdeSearchResult,
)
from knowde.feature.knowde.repo.clause import OrderBy, WherePhrase
from knowde.feature.knowde.repo.detail import fetch_knowdes_with_detail
from knowde.shared.cypher import Paging
from knowde.shared.errors import DomainError

from .cypher import q_adjacency_uids, q_stats, q_where_knowde


def search_total(
    s: str,
    where: WherePhrase = WherePhrase.CONTAINS,
) -> int:
    """検索文字列にマッチするknowde総数."""
    q_tot = f"""
        CALL () {{
        {q_where_knowde(where)}
        }}
        RETURN COUNT(sent)
    """
    res = db.cypher_query(
        q_tot,
        params={"s": s},
    )

    try:
        return res[0][0][0]
    except IndexError as e:
        msg = "Failed to get total count from query result."
        raise DomainError(msg=msg, status_code=status.HTTP_502_BAD_GATEWAY) from e


async def search_knowde(
    s: str,
    where: WherePhrase = WherePhrase.CONTAINS,
    paging: Paging = Paging(),
    order_by: OrderBy | None = OrderBy(),
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> KnowdeSearchResult:
    """用語、文のいずれかでマッチするものを返す."""
    q = rf"""
        CALL () {{
        {indent(q_where_knowde(where), " " * 4)}
        }}
        WITH sent // 中間結果のサイズダウン
        {q_stats("sent", order_by)}
        {(order_by.phrase() if order_by else "")}
        {paging.phrase()}
        RETURN
            sent.uid AS sent_uid
        """
    if do_print:
        print(q)  # noqa: T201
    rows, _ = db.cypher_query(q, params={"s": s})
    uids = res2uidstrs(rows)
    d = await fetch_knowdes_with_detail(uids, order_by=order_by)
    ls: list[Knowde] = []
    for row in rows:
        sent_uid = row[0]
        kst = d[sent_uid]
        ls.append(kst)
    return KnowdeSearchResult(
        total=search_total(s, where),
        data=ls,
        resource_infos=await resource_infos_by_resource_uids({
            k.resource_uid for k in ls
        }),
    )


def res2uidstrs(res: tuple) -> set[str]:
    """neo4j レスポンスからuuidのセットを返す."""

    def is_valid_uuid(uuid_string) -> bool:
        try:
            UUID(uuid_string)
            return True  # noqa: TRY300
        except ValueError:
            return False
        except TypeError:
            return False

    return set(filter(is_valid_uuid, collapse(res, base_type=UUID)))


async def adjacency_knowde(sent_uid: str) -> list[KAdjacency]:
    """隣接knowdeを返す."""
    q = rf"""
        MATCH (sent: Sentence {{uid: $uid}})
        {q_adjacency_uids("sent")}
        RETURN
            sent.uid as sent_uid
            , premises
            , conclusions
            , refers
            , referreds
            , details
            , abstracts
            , examples
        """
    res = await adb.cypher_query(q, params={"uid": sent_uid})
    uids = res2uidstrs(res)
    knowdes = await fetch_knowdes_with_detail(list(uids))
    ls = []
    for row in res[0]:
        (
            sent,
            premises,
            conclusions,
            refers,
            referreds,
            details,
            abstracts,
            examples,
        ) = row
        adj = KAdjacency(
            center=knowdes[sent],
            details=[knowdes[d] for d in details],
            premises=[knowdes[p] for p in premises],
            conclusions=[knowdes[c] for c in conclusions],
            refers=[knowdes[r] for r in refers],
            referreds=[knowdes[r] for r in referreds],
            abstracts=[knowdes[a] for a in abstracts],
            examples=[knowdes[e] for e in examples],
        )
        ls.append(adj)
    return ls
