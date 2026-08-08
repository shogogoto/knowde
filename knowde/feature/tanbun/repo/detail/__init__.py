"""detail repo."""

import operator
from collections import OrderedDict
from collections.abc import Iterable
from functools import reduce
from uuid import UUID

import networkx as nx
from more_itertools import flatten
from neomodel import adb, db

from knowde.feature.domain.errors import NotFoundError, NotUniqueError
from knowde.feature.domain.graph.edge_type import EdgeType
from knowde.feature.domain.types import UUIDy, to_uuid
from knowde.feature.parsing.primitive.term import Term
from knowde.feature.repo.cypher import q_call_term_names
from knowde.feature.tanbun.domain import (
    Additional,
    Tanbun,
    TanbunChain,
    TanbunChains,
    TanbunLocation,
)
from knowde.feature.tanbun.label import LQuoterm, LSentence
from knowde.feature.tanbun.repo.clause import OrderBy
from knowde.feature.tanbun.repo.cypher import (
    build_location_res,
    q_chain,
    q_location,
    q_stats,
    q_upper,
)


def q_tanbun_detail(
    with_location: bool = False,  # noqa: FBT001, FBT002
    order_by: OrderBy | None = OrderBy(),
) -> str:
    """Detail with location or not Query."""
    q_loc = q_location("sent") if with_location else ""
    return f"""
        // q_detail_location
        UNWIND $uids as uid
        MATCH (sent: Sentence {{uid: uid}})
        {q_call_term_names("sent")}
        {q_stats("sent", order_by)}
        OPTIONAL MATCH (intv: Interval)<-[:WHEN]-(sent)
        {q_loc}
        RETURN sent
            , names
            , alias
            , intv
            , stats
            {", location" if with_location else ""}
    """


def _row2tanbun(sent, names, alias, when, stats) -> Tanbun:
    """q_detail_locationの結果をTanbunに変換."""
    names = [n.get("val") for n in names] if names is not None else []
    return Tanbun(
        sentence=sent.get("val"),
        uid=sent.get("uid"),
        term=Term.create(*names, alias=alias) if names else None,
        stats=stats,
        additional=Additional(
            when=when.get("val") if when is not None else None,
        ),
        resource_uid=to_uuid(sent.get("resource_uid")),
    )


async def fetch_tanbuns_with_detail(
    uids: Iterable[UUIDy],
    order_by: OrderBy | None = OrderBy(),
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> dict[str, Tanbun]:
    """文のuuidリストから名前などの付属情報を返す."""
    q = q_tanbun_detail(order_by=order_by)
    if do_print:
        print(q)  # noqa: T201
    rows, _ = await adb.cypher_query(
        q,
        params={"uids": [to_uuid(uid).hex for uid in uids]},
    )
    d = OrderedDict()
    for row in rows:
        sent, names, alias, when, stats = row
        uid = sent.get("uid")
        d[uid] = _row2tanbun(sent, names, alias, when, stats)
    diff = set(uids) - set(d.keys())
    if len(diff) > 0:
        msg = f"単文取得に{len(diff)}個の漏れがある: {list(diff)}"
        raise NotFoundError(msg)
    return d


async def fetch_tanbuns_with_detail_and_location(
    uids: Iterable[UUIDy],
    order_by: OrderBy | None = OrderBy(),
) -> dict[str, tuple[Tanbun, TanbunLocation]]:
    """詳細とlocation付きで返す."""
    q = q_tanbun_detail(with_location=True, order_by=order_by)
    rows, _ = db.cypher_query(
        q,
        params={"uids": [to_uuid(uid).hex for uid in uids]},
    )

    def _to_tanbun():
        d = {}
        d_loc = {}
        d_parents = {}
        for row in rows:
            sent, names, alais, when, stats, location = row
            s, uid = sent.get("val"), sent.get("uid")
            if location is None:
                msg = f"location not found: {s} @{uid}"
                raise NotFoundError(msg)
            d[uid] = _row2tanbun(sent, names, alais, when, stats)
            d_loc[uid], d_parents[uid] = build_location_res(location, uid)
        return d, d_loc, d_parents

    d, d_loc, d_parents = _to_tanbun()
    # それぞれの parents を集めて一括 parent detial取得
    puids = set(flatten(d_parents.values()))
    parent_dk = await fetch_tanbuns_with_detail(puids)
    retval = {}
    for k, v in d.items():
        parents = [parent_dk[uid] for uid in d_parents[k]]
        retval[k] = (
            v,
            TanbunLocation(
                parents=parents,
                user=d_loc[k].user,
                folders=d_loc[k].folders,
                resource=d_loc[k].resource,
                headers=d_loc[k].headers,
            ),
        )
    return retval


def tanbun_upper(uid: UUID) -> LSentence:
    """単文の親を返す."""
    q = f"""
        MATCH (sent: Sentence {{uid: $uid}})
        {q_upper("sent")}
        RETURN upper
    """

    rows, _ = db.cypher_query(q, params={"uid": uid.hex})
    if len(rows) != 1:
        msg = f"{uid} sentence location is not unique: {len(rows)}"
        raise NotUniqueError(msg)
    return LSentence(**rows[0][0]._properties)  # noqa: SLF001


async def fetch_tanbun_chains(
    uids: Iterable[UUIDy],
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> TanbunChains:
    """単文の依存chain全てを含めた詳細."""
    q = f"""
        UNWIND $uids AS uid
        MATCH (s: Sentence {{uid: uid}})
        OPTIONAL MATCH (s)<-[:QUOTERM]-(qt: Quoterm)
        WITH COLLECT(qt) AS qts, s
        UNWIND [s] + qts AS sent
        WITH DISTINCT sent, s
        CALL (sent) {{
            // detail がない場合にsentが返らなくなるのを防ぐ
            RETURN (sent) as start, null as end, null as type
            UNION
            // Part Chain
            MATCH (sent)-[r:BELOW]->(:Sentence|Quoterm)
            RETURN startNode(r) as start, endNode(r) as end, type(r) as type
            UNION
            MATCH (sent)-[:BELOW]->(below:Sentence|Quoterm)
                -[rs:SIBLING|BELOW]->*(:Sentence|Quoterm)
            UNWIND rs as r
            RETURN startNode(r) as start, endNode(r) as end, type(r) as type
            UNION
            // Logic Chain
            {q_chain("sent", EdgeType.TO, indent_len=4)}
            UNION
            {q_chain("sent", EdgeType.RESOLVED, indent_len=4)}
            UNION
            {q_chain("sent", EdgeType.EXAMPLE, indent_len=4)}
        }}
        RETURN s.uid, start, end, type
    """
    uids = [to_uuid(uid).hex for uid in uids]
    if do_print:
        print(q)  # noqa: T201

    rows, _ = db.cypher_query(q, params={"uids": uids}, resolve_objects=True)
    g_dict = {uid: nx.MultiDiGraph() for uid in uids}
    for row in rows:
        tgt_uid, start, end, type_ = row
        g = g_dict[tgt_uid]
        start = tgt_uid if isinstance(start, LQuoterm) else start.uid
        if type_ is None:
            g.add_node(start)
            continue
        end = tgt_uid if isinstance(end, LQuoterm) else end.uid
        t: EdgeType = getattr(EdgeType, type_)
        t.add_edge(g, start, end)

    for g in g_dict.values():
        if len(g.nodes) == 0:
            msg = f"{uids[0]} sentence not found"
            raise NotFoundError(msg)
    nodes = reduce(operator.or_, [set(g.nodes) for g in g_dict.values()])
    d = await fetch_tanbuns_with_detail(nodes, do_print=do_print)
    d2 = await fetch_tanbuns_with_detail_and_location(uids)
    return TanbunChains(
        root=[
            TanbunChain(
                uid=to_uuid(uid),
                g=g_dict[uid],
                knowdes={n: d[n] for n in g_dict[uid].nodes},
                location=d2[uid][1],
            )
            for uid in uids
        ],
    )
