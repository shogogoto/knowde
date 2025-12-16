"""detail repo."""

from collections.abc import Iterable
from uuid import UUID

import networkx as nx
from more_itertools import flatten
from neomodel import adb, db

from knowde.feature.knowde import (
    Additional,
    Knowde,
    KnowdeDetail,
    KnowdeLocation,
)
from knowde.feature.knowde.repo.clause import OrderBy
from knowde.feature.knowde.repo.cypher import (
    build_location_res,
    q_call_sent_names,
    q_chain,
    q_location,
    q_stats,
    q_upper,
)
from knowde.feature.parsing.primitive.term import Term
from knowde.shared.errors.domain import NotFoundError, NotUniqueError
from knowde.shared.knowde.label import LQuoterm, LSentence
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.types import UUIDy, to_uuid


def q_detail_location(
    is_location: bool = False,  # noqa: FBT001, FBT002
    order_by: OrderBy | None = OrderBy(),
) -> str:
    """Detail with location or not Query."""
    q_loc = q_location("sent") if is_location else ""
    return f"""
        // q_detail_location
        UNWIND $uids as uid
        MATCH (sent: Sentence {{uid: uid}})
        {q_call_sent_names("sent")}
        {q_stats("sent", order_by)}
        OPTIONAL MATCH (intv: Interval)<-[:WHEN]-(sent)
        {q_loc}
        RETURN sent
            , names
            , alias
            , intv
            , stats
            {", location" if is_location else ""}
    """


def _row2knowde(sent, names, alias, when, stats) -> Knowde:
    """q_detail_locationの結果をKnowdeに変換."""
    names = [n.get("val") for n in names] if names is not None else []
    return Knowde(
        sentence=sent.get("val"),
        uid=sent.get("uid"),
        term=Term.create(*names, alias=alias) if names else None,
        stats=stats,
        additional=Additional(
            when=when.get("val") if when is not None else None,
        ),
        resource_uid=to_uuid(sent.get("resource_uid")),
    )


async def fetch_knowdes_with_detail(
    uids: Iterable[UUIDy],
    order_by: OrderBy | None = OrderBy(),
    do_print: bool = False,  # noqa: FBT001, FBT002
) -> dict[UUID, Knowde]:
    """文のuuidリストから名前などの付属情報を返す."""
    q = q_detail_location(order_by=order_by)
    if do_print:
        print(q)  # noqa: T201
    rows, _ = await adb.cypher_query(
        q,
        params={"uids": [to_uuid(uid).hex for uid in uids]},
    )
    d = {}
    for row in rows:
        sent, names, alias, when, stats = row
        uid = sent.get("uid")
        d[uid] = _row2knowde(sent, names, alias, when, stats)
    diff = set(uids) - set(d.keys())
    if len(diff) > 0:
        msg = f"knowde取得に{len(diff)}個の漏れがある: {list(diff)}"
        raise NotFoundError(msg)
    return d


async def fetch_knowdes_with_detail_and_location(
    uids: Iterable[str],
    order_by: OrderBy | None = OrderBy(),
) -> dict[str, tuple[Knowde, KnowdeLocation]]:
    """詳細とlocation付きで返す."""
    q = q_detail_location(is_location=True, order_by=order_by)
    rows, _ = db.cypher_query(q, params={"uids": list(uids)})

    def _to_knowde():
        d = {}
        d_loc = {}
        d_parents = {}
        for row in rows:
            sent, names, alais, when, stats, location = row
            s, uid = sent.get("val"), sent.get("uid")
            if location is None:
                msg = f"location not found: {s} @{uid}"
                raise NotFoundError(msg)
            d[uid] = _row2knowde(sent, names, alais, when, stats)
            d_loc[uid], d_parents[uid] = build_location_res(location, uid)
        return d, d_loc, d_parents

    d, d_loc, d_parents = _to_knowde()
    # それぞれの parents を集めて一括 parent detial取得
    puids = set(flatten(d_parents.values()))
    parent_dk = await fetch_knowdes_with_detail(puids)
    retval = {}
    for k, v in d.items():
        parents = [parent_dk[uid] for uid in d_parents[k]]
        retval[k] = (
            v,
            KnowdeLocation(
                parents=parents,
                user=d_loc[k].user,
                folders=d_loc[k].folders,
                resource=d_loc[k].resource,
                headers=d_loc[k].headers,
            ),
        )
    return retval


def knowde_upper(uid: UUID) -> LSentence:
    """knowdeの親を返す."""
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


async def chains_knowde(uid: UUID, do_print: bool = False) -> KnowdeDetail:  # noqa: FBT001, FBT002
    """knowdeの依存chain全てを含めた詳細."""
    q = f"""
        MATCH (s: Sentence {{uid: $uid}})
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
        RETURN start, end, type
        """
    if do_print:
        print(q)  # noqa: T201
    rows, _ = db.cypher_query(
        q,
        params={"uid": uid.hex},
        resolve_objects=True,
    )
    g = nx.MultiDiGraph()
    d = {}
    for row in rows:
        start, end, type_ = row
        start = uid.hex if isinstance(start, LQuoterm) else start.uid
        if type_ is None:
            g.add_node(start)
            continue
        end = uid.hex if isinstance(end, LQuoterm) else end.uid
        t: EdgeType = getattr(EdgeType, type_)
        t.add_edge(g, start, end)

    if len(g.nodes) == 0:
        msg = f"{uid} sentence not found"
        raise NotFoundError(msg)
    d = await fetch_knowdes_with_detail(g.nodes, do_print=do_print)
    d2 = await fetch_knowdes_with_detail_and_location([uid.hex])
    return KnowdeDetail(
        uid=uid,
        g=g,
        knowdes=d,
        location=d2[uid.hex][1],
    )
