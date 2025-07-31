"""detail repo."""

from collections.abc import Iterable
from uuid import UUID

import networkx as nx
from more_itertools import flatten
from neomodel import db

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
    q_location,
    q_stats,
    q_upper,
)
from knowde.feature.parsing.primitive.term import Term
from knowde.feature.stats.nxdb import LSentence
from knowde.shared.errors.domain import NotFoundError, NotUniqueError
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.types import to_uuid


def q_detail_location(
    is_location: bool = False,  # noqa: FBT001, FBT002
    order_by: OrderBy | None = OrderBy(),
) -> str:
    """Detail with location or not Query."""
    q_loc = q_location("sent") if is_location else ""
    return f"""
        UNWIND $uids as uid
        MATCH (sent: Sentence {{uid: uid}})
        {q_call_sent_names("sent")}
        {q_stats("sent", order_by)}
        OPTIONAL MATCH (intv: Interval)<-[:WHEN]-(sent)
        {q_loc}
        RETURN sent
            , names
            , intv
            , stats
            {", location" if is_location else ""}
    """


def fetch_knowdes_with_detail(
    uids: Iterable[str],
    order_by: OrderBy | None = OrderBy(),
) -> dict[str, Knowde]:
    """文のuuidリストから名前などの付属情報を返す."""
    q = q_detail_location(order_by=order_by)
    res = db.cypher_query(q, params={"uids": list(uids)})
    d = {}
    for row in res[0]:
        sent, names, when, stats = row
        uid = sent.get("uid")
        names = [n.get("val") for n in names] if names is not None else []
        d[uid] = Knowde(
            sentence=sent.get("val"),
            uid=uid,
            term=Term.create(*names) if names else None,
            stats=stats,
            additional=Additional(
                when=when.get("val") if when is not None else None,
            ),
            resource_uid=to_uuid(sent.get("resource_uid")),
        )

    diff = set(uids) - set(d.keys())
    if len(diff) > 0:
        msg = f"fail to fetch_nodes_by_ids: {[UUID(e) for e in diff]}"
        raise NotFoundError(msg)
    return d


def fetch_knowdes_with_detail_and_location(
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
            sent, names, when, stats, location = row
            s, uid = sent.get("val"), sent.get("uid")
            if location is None:
                msg = f"location not found: {s} @{uid}"
                raise NotFoundError(msg)
            names = [n.get("val") for n in names] if names is not None else []
            d[uid] = Knowde(
                sentence=s,
                uid=uid,
                term=Term.create(*names) if names else None,
                stats=stats,
                additional=Additional(
                    when=when.get("val") if when is not None else None,
                ),
                resource_uid=to_uuid(sent.get("resource_uid")),
            )
            d_loc[uid], d_parents[uid] = build_location_res(location)
        return d, d_loc, d_parents

    d, d_loc, d_parents = _to_knowde()
    # それぞれの parents を集めて一括 parent detial取得
    puids = set(flatten(d_parents.values()))
    parent_dk = fetch_knowdes_with_detail(puids)
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
        msg = f"{uid} sentence location not found"
        raise NotUniqueError(msg)
    return LSentence(**rows[0][0]._properties)  # noqa: SLF001


def chains_knowde(uid: UUID, do_print: bool = False) -> KnowdeDetail:  # noqa: FBT001, FBT002
    """knowdeの依存chain全てを含めた詳細."""
    q = """
        MATCH (sent: Sentence {uid: $uid})
        CALL (sent) {
            // detail がない場合にMATCHしなくなる
            RETURN (sent) as start, null as end, null as type
            UNION
            // Part Chain
            MATCH (sent)-[r:BELOW]->(:Sentence)
            RETURN startNode(r) as start, endNode(r) as end, type(r) as type
            UNION
            MATCH (sent)-[:BELOW]->(below:Sentence)
                -[rs:SIBLING|BELOW]->*(:Sentence)
            UNWIND rs as r
            RETURN startNode(r) as start, endNode(r) as end, type(r) as type
            UNION
            // Logic Chain
            MATCH (p1:Sentence)-[r:TO]-(p2:Sentence)-[:TO]-*(sent)
            RETURN startNode(r) as start, endNode(r) as end, type(r) as type
            UNION
            // Ref Chain
            MATCH (:Sentence)-[r:RESOLVED]-(:Sentence)
                -[:RESOLVED]-*(sent)
            RETURN startNode(r) as start, endNode(r) as end, type(r) as type
        }
        RETURN start, end, type
        """
    if do_print:
        print(q)  # noqa: T201
    res = db.cypher_query(
        q,
        params={"uid": uid.hex},
        resolve_objects=True,
    )
    g = nx.MultiDiGraph()
    for row in res[0]:
        start, end, type_ = row
        if type_ is None:
            g.add_node(start.uid)
            continue
        t: EdgeType = getattr(EdgeType, type_)
        t.add_edge(g, start.uid, end.uid)

    if len(g.nodes) == 0:
        msg = f"{uid} sentence not found"
        raise NotFoundError(msg)

    d = fetch_knowdes_with_detail(g.nodes)
    d2 = fetch_knowdes_with_detail_and_location([uid.hex])
    return KnowdeDetail(
        uid=uid,
        g=g,
        knowdes={to_uuid(k): v for k, v in d.items()},
        location=d2[uid.hex][1],
    )
