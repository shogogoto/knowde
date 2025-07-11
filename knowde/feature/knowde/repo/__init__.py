"""repo."""

from datetime import datetime
from uuid import UUID

from fastapi import status
from more_itertools import collapse
from neomodel import db

from knowde.feature.entry.category.folder.repo import fetch_namespace
from knowde.feature.entry.mapper import MResource
from knowde.feature.entry.namespace import save_resource
from knowde.feature.entry.namespace.sync import txt2meta
from knowde.feature.knowde import KnowdeWithStats, KStats
from knowde.feature.knowde.repo.clause import OrderBy, Paging, WherePhrase
from knowde.feature.knowde.repo.detail import (
    fetch_knowde_additionals_by_ids,
)
from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.tree2net import parse2net
from knowde.feature.stats.nxdb.save import sn2db
from knowde.shared.errors import DomainError
from knowde.shared.types import UUIDy, to_uuid

from .cypher import q_adjaceny_uids, q_call_sent_names, q_stats, q_where_knowde


async def save_text(
    user_id: UUIDy,
    s: str,
    path: tuple[str, ...] | None = None,
    updated: datetime | None = None,
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> tuple[SysNet, MResource]:
    """テキストを保存."""
    meta = txt2meta(s)
    meta.updated = updated
    meta.path = path
    ns = await fetch_namespace(to_uuid(user_id))
    await save_resource(meta, ns)
    r = ns.get_resource(meta.title)
    sn = parse2net(s)
    sn2db(sn, r.uid, do_print=do_print)
    return sn, r


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


def search_knowde(
    s: str,
    where: WherePhrase = WherePhrase.CONTAINS,
    paging: Paging = Paging(),
    order_by: OrderBy | None = OrderBy(),
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> tuple[int, list[KnowdeWithStats]]:
    """用語、文のいずれかでマッチするものを返す."""
    q = rf"""
        CALL () {{
        {q_where_knowde(where)}
        }}
        WITH sent // 中間結果のサイズダウン
        CALL (sent) {{
        {q_stats("sent", order_by)}
        }}
        // {q_adjaceny_uids("sent")}
        {(order_by.phrase() if order_by else "")}
        {paging.phrase()}
        {q_call_sent_names("sent")}
        OPTIONAL MATCH (intv: Interval)<-[:WHEN]-(sent)
        RETURN
            sent.uid AS sent_uid
            , stats
        """
    if do_print:
        print(q)  # noqa: T201
    res = db.cypher_query(q, params={"s": s})
    uids = res2uidstrs(res)
    d = fetch_knowde_additionals_by_ids(uids)
    ls = []
    for row in res[0]:
        sent_uid, stats = row
        kst = KnowdeWithStats(
            knowde=d[sent_uid],
            stats=KStats.model_validate(stats),
        )
        ls.append(kst)
    total = search_total(s, where)
    return total, ls


def res2uidstrs(res: tuple) -> set[str]:
    """neo4j レスポンスからuuidのセットを返す."""

    def is_valid_uuid(uuid_string) -> bool:
        try:
            # print("#" * 80)
            # print(uuid_string)
            UUID(uuid_string)
            return True  # noqa: TRY300
        except ValueError:
            return False
        except TypeError:
            return False

    return set(filter(is_valid_uuid, collapse(res, base_type=UUID)))


# def res2adjacency(res: tuple):
#     """dbレスポンスからpydanticに変換."""
#     uids = res2uidstrs(res)
#     knowdes = fetch_knowde_additionals_by_ids(list(uids))
#     ls = []
#     for row in res[0]:
#         (
#             sent,
#             premises,
#             conclusions,
#             refers,
#             referreds,
#             details,
#             stats,
#         ) = row
#         adj = KAdjacency(
#             center=knowdes[sent],
#             details=[knowdes[d] for d in details[0]],
#             premises=[knowdes[p] for p in premises[0]],
#             conclusions=[knowdes[c] for c in conclusions[0]],
#             refers=[knowdes[r] for r in refers[0]],
#             referreds=[knowdes[r] for r in referreds[0]],
#             stats=KStats.model_validate(stats),
#         )
#         ls.append(adj)
#     total = search_total(s, wp)
#     return total, ls


# def get_adjacency(
#     s: str,
#     where: WherePhrase = WherePhrase.CONTAINS,
# ):
#     q = rf"""
#         MATCH (sent: Sentence {{uid: $uid}})
#         {q_adjaceny_uids("sent")}
#         {q_call_sent_names("sent")}
#         OPTIONAL MATCH (intv: Interval)<-[:WHEN]-(sent)
#         RETURN
#             sent
#             , names
#             , intv
#             , stats
#         """
#     res = db.cypher_query(q, params={"s": s})
#     return res2adjacency(res)
