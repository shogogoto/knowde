"""repo."""

from typing import Any
from uuid import UUID

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
from knowde.feature.knowde.repo.adj import AdjType
from knowde.feature.knowde.repo.clause import OrderBy, WherePhrase
from knowde.feature.knowde.repo.detail import fetch_knowdes_with_detail
from knowde.shared.cypher import Paging
from knowde.shared.errors import DomainError as DomainError
from knowde.shared.types import UUIDy, to_uuid

from .cypher import q_adjacency_uids, q_search
from .cypher import q_stats as q_stats
from .cypher import q_where_knowde as q_where_knowde


def search_total(
    s: str,
    where: WherePhrase = WherePhrase.CONTAINS,
    filter_resource_uids: list[UUIDy] | None = None,
    only_with_term: bool = False,  # noqa: FBT001, FBT002
) -> int:
    """検索文字列にマッチするknowde総数."""
    q = q_search(where, filter_resource_uids, only_with_term)
    q += """
        RETURN COUNT(sent)
    """
    res = db.cypher_query(
        q,
        params={
            "s": s,
            "resource_uids": [to_uuid(uid).hex for uid in filter_resource_uids]
            if filter_resource_uids
            else [],
        },
    )
    return res[0][0][0]


async def search_knowde_ids(  # noqa: PLR0917
    s: str,
    where: WherePhrase = WherePhrase.CONTAINS,
    paging: Paging = Paging(),
    order_by: OrderBy | None = OrderBy(),
    belong_resource_uids: list[UUIDy] | None = None,
    only_with_term: bool = False,  # noqa: FBT001, FBT002
    exclude_sent_ids: list[UUIDy] | None = None,
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> list[UUID]:
    """用語、文のいずれかでマッチする単文のUUIDを返す."""
    q = q_search(
        where,
        belong_resource_uids,
        only_with_term,
        exclude_sent_ids=exclude_sent_ids,
    )
    q += f"""
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
            "resource_uids": [to_uuid(uid).hex for uid in belong_resource_uids]
            if belong_resource_uids
            else [],
            "exclude_uids": [to_uuid(uid).hex for uid in exclude_sent_ids]
            if exclude_sent_ids
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
    only_with_term: bool = False,  # noqa: FBT001, FBT002
    exclude_sent_ids: list[UUIDy] | None = None,
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> KnowdeSearchResult:
    """用語、文のいずれかでマッチする単文の検索結果を返す."""
    kn_uids = await search_knowde_ids(
        s,
        where,
        paging,
        order_by,
        filter_resource_uids,
        only_with_term,
        exclude_sent_ids,
        do_print,
    )
    d = await fetch_knowdes_with_detail(kn_uids, order_by=order_by)
    ls = list(d.values())
    return KnowdeSearchResult(
        total=search_total(s, where, filter_resource_uids, only_with_term),
        data=ls,
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


async def adj_knowde_ids(
    sent_uids: list[UUIDy],
    radius: int = 1,
    only_with_term: bool = False,  # noqa: FBT001, FBT002
    types: list[AdjType] | None = None,
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> tuple[list[UUID], Any]:
    """隣接knowdeのidを返す."""
    q_term = "<-[:DEF]-(:Term)" if only_with_term else ""
    q = rf"""
        UNWIND $uids AS uid
        MATCH (sent: Sentence {{uid: uid}})
            {q_term}
        {q_adjacency_uids("sent", "sent", radius)}
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
    return res2uidstrs(rows), rows


async def adj_knowde(
    sent_uids: list[UUIDy],
    radius: int = 1,
    only_with_term: bool = False,  # noqa: FBT001, FBT002
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> list[KAdjacency]:
    """隣接knowdeを返す."""
    uids, rows = await adj_knowde_ids(sent_uids, radius, only_with_term, do_print)
    knowdes = await fetch_knowdes_with_detail(uids)
    ls = []
    for row in rows:
        sent, premises, conclusions, refers, referreds, details, abstracts, examples = (
            row
        )
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
