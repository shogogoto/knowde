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
from knowde.feature.knowde import KAdjacency, Knowde
from knowde.feature.knowde.repo.clause import OrderBy, Paging, WherePhrase
from knowde.feature.knowde.repo.detail import fetch_knowdes_with_detail
from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.parsing.tree2net import parse2net
from knowde.feature.stats.nxdb.save import sn2db
from knowde.shared.errors import DomainError
from knowde.shared.types import UUIDy, to_uuid

from .cypher import q_adjaceny_uids, q_stats, q_where_knowde


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
) -> tuple[int, list[Knowde]]:
    """用語、文のいずれかでマッチするものを返す."""
    q = rf"""
        CALL () {{
        {q_where_knowde(where)}
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
    d = fetch_knowdes_with_detail(uids)
    ls: list[Knowde] = []
    for row in rows:
        sent_uid = row[0]
        kst = d[sent_uid]
        ls.append(kst)
    return search_total(s, where), ls


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


def adjacency_knowde(sent_uid: str) -> list[KAdjacency]:
    """隣接knowdeを返す."""
    q = rf"""
        MATCH (sent: Sentence {{uid: $uid}})
        {q_adjaceny_uids("sent")}
        RETURN
            sent.uid as sent_uid
            , premises
            , conclusions
            , refers
            , referreds
            , details
        """
    res = db.cypher_query(q, params={"uid": sent_uid})
    uids = res2uidstrs(res)
    knowdes = fetch_knowdes_with_detail(list(uids))
    ls = []
    for row in res[0]:
        (
            sent,
            premises,
            conclusions,
            refers,
            referreds,
            details,
        ) = row
        adj = KAdjacency(
            center=knowdes[sent],
            details=[knowdes[d] for d in details],
            premises=[knowdes[p] for p in premises],
            conclusions=[knowdes[c] for c in conclusions],
            refers=[knowdes[r] for r in refers],
            referreds=[knowdes[r] for r in referreds],
        )
        ls.append(adj)
    return ls
