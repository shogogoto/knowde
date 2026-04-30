"""repo."""

from textwrap import indent
from uuid import UUID

from fastapi import status
from more_itertools import collapse
from neomodel import adb, db

from knowde.feature.entry.namespace import resource_infos_by_resource_uids
from knowde.feature.knowde import (
    KAdjacency,
    KnowdeSearchResult,
)
from knowde.feature.knowde import (
    Knowde as Knowde,
)
from knowde.feature.knowde.repo.clause import OrderBy, WherePhrase
from knowde.feature.knowde.repo.detail import fetch_knowdes_with_detail
from knowde.shared.cypher import Paging
from knowde.shared.errors import DomainError
from knowde.shared.types import UUIDy, to_uuid

from .cypher import q_adjacency_uids, q_stats, q_where_knowde


def search_total(
    s: str,
    where: WherePhrase = WherePhrase.CONTAINS,
    resource_uids: list[UUIDy] | None = None,
) -> int:
    """検索文字列にマッチするknowde総数."""
    q_rsrc = (
        ""
        if resource_uids is None or len(resource_uids) == 0
        else """
        WHERE sent.resource_uid IN $resource_uids
    """
    )
    q_tot = f"""
        CALL () {{
        {q_where_knowde(where)}
        }}
        WITH sent
            {q_rsrc}
        RETURN COUNT(sent)
    """
    res = db.cypher_query(
        q_tot,
        params={
            "s": s,
            "resource_uids": [to_uuid(uid).hex for uid in resource_uids]
            if resource_uids
            else [],
        },
    )

    try:
        return res[0][0][0]
    except IndexError as e:
        msg = "Failed to get total count from query result."
        err = DomainError(msg=msg)
        err.status_code = status.HTTP_502_BAD_GATEWAY
        raise err from e


async def search_knowde_ids(  # noqa: PLR0917
    s: str,
    where: WherePhrase = WherePhrase.CONTAINS,
    paging: Paging = Paging(),
    order_by: OrderBy | None = OrderBy(),
    filter_resource_uids: list[UUIDy] | None = None,
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> list[UUID]:
    """用語、文のいずれかでマッチする単文のUUIDを返す."""
    q_rsrc = (
        ""
        if filter_resource_uids is None or len(filter_resource_uids) == 0
        else """
        WHERE sent.resource_uid IN $resource_uids
    """
    )

    q = rf"""
        CALL () {{
        {indent(q_where_knowde(where), " " * 4)}
        }}
        WITH sent // 中間結果のサイズダウン
            {q_rsrc}
        {q_stats("sent", order_by)}
        {(order_by.phrase() if order_by else "")}
        {paging.phrase()}
        RETURN
            sent.uid AS sent_uid
        """
    if do_print:
        print(q)  # noqa: T201
    rows, _ = await adb.cypher_query(
        q,
        params={
            "s": s,
            "resource_uids": [to_uuid(uid).hex for uid in filter_resource_uids]
            if filter_resource_uids
            else [],
        },
    )
    return res2uidstrs(rows)


async def search_knowde(  # noqa: PLR0917
    s: str,
    where: WherePhrase = WherePhrase.CONTAINS,
    paging: Paging = Paging(),
    order_by: OrderBy | None = OrderBy(),
    filter_resource_uids: list[UUIDy] | None = None,
    do_print: bool = False,  # noqa: FBT001, FBT002
):
    """用語、文のいずれかでマッチする単文の検索結果を返す."""
    kn_uids = await search_knowde_ids(
        s,
        where,
        paging,
        order_by,
        filter_resource_uids,
        do_print,
    )
    d = await fetch_knowdes_with_detail(kn_uids, order_by=order_by)
    ls = list(d.values())
    return KnowdeSearchResult(
        total=search_total(s, where, filter_resource_uids),
        data=list(d.values()),
        resource_infos=await resource_infos_by_resource_uids({
            k.resource_uid for k in ls
        }),
    )


def res2uidstrs(res: tuple) -> list[UUID]:
    """neo4j レスポンスからuuidのセットを返す."""

    def is_valid_uuid(uuid_string) -> bool:
        try:
            UUID(uuid_string)
            return True  # noqa: TRY300
        except ValueError:
            return False
        except TypeError:
            return False

    return list(filter(is_valid_uuid, collapse(res, base_type=UUID)))


async def adjacency_knowde(
    sent_uids: list[UUIDy],
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> list[KAdjacency]:
    """隣接knowdeを返す."""
    q = rf"""
        UNWIND $uids AS uid
        MATCH (sent: Sentence {{uid: uid}})
        {q_adjacency_uids("sent", "sent")}
        RETURN
            sent.uid AS sent_uid
            , premises
            , conclusions
            , refers
            , referreds
            , details
            , abstracts
            , examples
        """
    if do_print:
        print(q)  # noqa: T201
    rows, _ = await adb.cypher_query(
        q,
        params={"uids": [to_uuid(uid).hex for uid in sent_uids]},
    )
    uids = res2uidstrs(rows)
    knowdes = await fetch_knowdes_with_detail(list(uids))
    ls = []
    for row in rows:
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
