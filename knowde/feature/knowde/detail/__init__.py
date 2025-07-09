"""detail repo."""

from uuid import UUID

import networkx as nx
from more_itertools import first_true
from neomodel import db

from knowde.feature.entry.mapper import MResource
from knowde.feature.knowde import Knowde, KnowdeDetail, KnowdeLocation, UidStr
from knowde.feature.parsing.primitive.term import Term
from knowde.feature.user.domain import User
from knowde.shared.errors.domain import NotFoundError
from knowde.shared.nxutil.edge_type import EdgeType


# うまいクエリの方法が思いつかないので、別クエリに分ける
def fetch_knowde_by_ids(uids: list[str]) -> dict[UUID, Knowde]:
    """文のuuidリストから名前などの付属情報を返す."""
    q = """
        UNWIND $uids as uid
        MATCH (sent: Sentence {uid: uid})
        CALL (sent) {
            OPTIONAL MATCH p = (sent)-[:DEF|ALIAS]-*(:Term)
            WITH p, LENGTH(p) as len
            ORDER BY len DESC
            LIMIT 1
            RETURN nodes(p) as names
        }
        OPTIONAL MATCH (intv: Interval)<-[:WHEN]-(sent)
        RETURN sent
            , names[1..]
            , intv
    """
    res = db.cypher_query(q, params={"uids": uids})
    d = {}
    for row in res[0]:
        sent, names, when = row
        uid = sent.get("uid")
        names = [n.get("val") for n in names] if names is not None else []
        d[uid] = Knowde(
            sentence=sent.get("val"),
            uid=uid,
            term=Term.create(*names) if names else None,
            when=when.get("val") if when is not None else None,
        )

    diff = set(uids) - set(d.keys())
    if len(diff) > 0:
        msg = f"fail to fetch_nodes_by_ids: {[UUID(e) for e in diff]}"
        raise NotFoundError(msg)
    return d


def locate_knowde(uid: UUID, do_print: bool = False) -> KnowdeLocation:  # noqa: FBT001, FBT002
    """knowdeの親~userまでを返す."""
    q = """
        MATCH (sent: Sentence {uid: $uid})
            , p2 = (r:Resource)-[:SIBLING|BELOW|HEAD|NUM]->*(sent)
            , p = (user:User)-[:OWNED|PARENT]-*(r)
        RETURN nodes(p) + nodes(p2)[0..-1] as nodes
    """
    if do_print:
        print(q)  # noqa: T201
    res = db.cypher_query(q, params={"uid": uid.hex})
    if len(res[0]) == 0:
        msg = f"{uid} sentence location not found"
        raise NotFoundError(msg)

    for row in res[0][0]:
        row = list(dict.fromkeys(row))  # noqa: PLW2901 重複削除
        user = User.model_validate(dict(row[0]))
        r = first_true(row[1:], pred=lambda n: "Resource" in n.labels)
        r_i = row.index(r)
        folders = [UidStr(val=e.get("name"), uid=e.get("uid")) for e in row[1:r_i]]
        resource = MResource.freeze_dict(dict(r))

        first_sent = first_true(row, pred=lambda n: "Sentence" in n.labels)
        s_i = row.index(first_sent) if first_sent is not None else -1
        headers = [
            UidStr(val=e.get("val"), uid=e.get("uid")) for e in row[r_i + 1 : s_i]
        ]
        uids = [e.get("uid") for e in row[s_i:]] if s_i != -1 else []
        knowdes = fetch_knowde_by_ids(uids)
        parents = [knowdes[uid] for uid in uids]
        return KnowdeLocation(
            user=user,
            folders=folders,
            resource=resource,
            headers=headers,
            parents=parents,
        )
    raise ValueError


def detail_knowde(uid: UUID, do_print: bool = False) -> KnowdeDetail:  # noqa: FBT001, FBT002
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
        knowdes=fetch_knowde_by_ids(list(g.nodes)),
        location=locate_knowde(uid),
    )
