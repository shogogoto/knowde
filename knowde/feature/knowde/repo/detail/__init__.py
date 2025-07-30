"""detail repo."""

from collections.abc import Iterable
from uuid import UUID

import networkx as nx
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
)
from knowde.feature.parsing.primitive.term import Term
from knowde.shared.errors.domain import NotFoundError
from knowde.shared.nxutil.edge_type import EdgeType


# うまいクエリの方法が思いつかないので、別クエリに分ける
def fetch_knowde_additionals_by_ids(
    uids: Iterable[str],
    order_by: OrderBy | None = OrderBy(),
) -> dict[UUID, Knowde]:
    """文のuuidリストから名前などの付属情報を返す."""
    q = f"""
        UNWIND $uids as uid
        MATCH (sent: Sentence {{uid: uid}})
        {q_call_sent_names("sent")}
        {q_stats("sent", order_by)}
        OPTIONAL MATCH (intv: Interval)<-[:WHEN]-(sent)
        RETURN sent
            , names
            , intv
            , stats
    """
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
        )

    diff = set(uids) - set(d.keys())
    if len(diff) > 0:
        msg = f"fail to fetch_nodes_by_ids: {[UUID(e) for e in diff]}"
        raise NotFoundError(msg)
    return d


def locate_knowde(uid: UUID, do_print: bool = False) -> KnowdeLocation:  # noqa: FBT001, FBT002
    """knowdeの親~userまでを返す."""
    q = f"""
        MATCH (sent: Sentence {{uid: $uid}})
        {q_location("sent")}
    """
    if do_print:
        print(q)  # noqa: T201
    res = db.cypher_query(q, params={"uid": uid.hex})
    if len(res[0]) == 0:
        msg = f"{uid} sentence location not found"
        raise NotFoundError(msg)
    for row in res[0][0]:
        return build_location_res(row, fetch_knowde_additionals_by_ids)
    raise ValueError


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

    return KnowdeDetail(
        uid=uid,
        g=g,
        knowdes=fetch_knowde_additionals_by_ids(list(g.nodes)),
        location=locate_knowde(uid),
    )
