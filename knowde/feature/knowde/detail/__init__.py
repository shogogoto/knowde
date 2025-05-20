"""detail repo."""

from uuid import UUID

import networkx as nx
from more_itertools import first_true
from neomodel import db

from knowde.complex.entry.mapper import MResource
from knowde.feature.knowde import Knowde, KnowdeDetail, KnowdeLocation, UidStr
from knowde.primitive.__core__.errors.domain import NotFoundError
from knowde.primitive.__core__.nxutil.edge_type import EdgeType
from knowde.primitive.term import Term
from knowde.primitive.user import User


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
    return d


def locate_knowde(uid: UUID, do_print: bool = False) -> KnowdeLocation:  # noqa: FBT001, FBT002
    """knowdeの親~userまでを返す."""
    q = """
        MATCH (sent: Sentence {uid: $uid})
        MATCH p = (user:User)<-[:OWNED|PARENT]-*(r:Resource)
            -[:HEAD]->*(h:Head)
            -[:SIBLING|BELOW]->*(s:Sentence)
            -[:SIBLING|BELOW]->*(sent)
        OPTIONAL MATCH p_name = (s)-[:DEF|ALIAS]-*(:Term)
        RETURN nodes(p)
    """
    if do_print:
        print(q)  # noqa: T201
    res = db.cypher_query(q, params={"uid": uid.hex})
    if len(res[0]) == 0:
        msg = f"{uid} sentence location not found"
        raise NotFoundError(msg)

    for row in res[0][0]:
        user = User.model_validate(dict(row[0]))
        r = first_true(row[1:], pred=lambda n: "Resource" in n.labels)
        r_i = row.index(r)
        folders = [UidStr(val=e.get("name"), uid=e.get("uid")) for e in row[1:r_i]]
        resource = MResource.freeze_dict(dict(r))

        first_sent = first_true(row, pred=lambda n: "Sentence" in n.labels)
        s_i = row.index(first_sent)
        headers = [
            UidStr(val=e.get("val"), uid=e.get("uid")) for e in row[r_i + 1 : s_i]
        ]
        uids = [e.get("uid") for e in row[s_i:]]
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
            // detail
            MATCH (sent)-[:BELOW]->(:Sentence)-[:SIBLING|BELOW]->*(b1:Sentence)
                -[r:SIBLING|BELOW]->(b2:Sentence)
            RETURN b1 as start, b2 as end, type(r) as type
            UNION
            WITH sent
            // Logic Chain
            MATCH (p1:Sentence)-[r:TO]-(p2:Sentence)-[:TO]-*(sent)
            RETURN startNode(r) as start, endNode(r) as end, type(r) as type
            UNION
            WITH sent
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

    if len(res[0]) == 0:
        msg = f"{uid} not found"
        raise NotFoundError(msg)
    g = nx.MultiDiGraph()
    for row in res[0]:
        start, end, type_ = row
        t: EdgeType = getattr(EdgeType, type_)
        t.add_edge(g, start.uid, end.uid)
    return KnowdeDetail(
        uid=uid,
        g=g,
        knowdes=fetch_knowde_by_ids(list(g.nodes)),
        location=locate_knowde(uid),
    )
