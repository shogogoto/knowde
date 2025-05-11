"""detail repo."""

from typing import Any
from uuid import UUID

import networkx as nx
from neomodel import db

from knowde.complex.__core__.sysnet.sysnode import Def
from knowde.complex.__core__.sysnet.sysnode.merged_def import MergedDef
from knowde.feature.knowde import KnowdeDetail
from knowde.primitive.__core__.nxutil.edge_type import EdgeType


def detail_knowde(uid: UUID, do_print: bool = False) -> KnowdeDetail:  # noqa: FBT001, FBT002, PLR0914
    """knowdeの依存chain全てを含めた詳細."""
    # + q_root_path("sent", "p_premise", EdgeType.TO.name)
    # + q_leaf_path("sent", "p_conclution", EdgeType.TO.name)
    # + q_root_path("sent", "p_referred", EdgeType.RESOLVED.name)
    # + q_leaf_path("sent", "p_refer", EdgeType.RESOLVED.name)
    # + q_leaf_path("sent", "p_detail", "BELOW|SIBLING")
    q = """
        MATCH (sent: Sentence {uid: $uid})
        CALL {
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

        OPTIONAL MATCH (intv: Interval)<-[:WHEN]-(sent)
        OPTIONAL MATCH (start)<-[:DEF]-(:Term)-[:ALIAS]-*(start_name:Term)
        OPTIONAL MATCH (end)<-[:DEF]-(:Term)-[:ALIAS]-*(end_name:Term)

        // meta data
        OPTIONAL MATCH (start_intv: Interval)<-[:WHEN]-(start)
        OPTIONAL MATCH (end_intv: Interval)<-[:WHEN]-(end)

        // MATCH p_parent = (user: User)-[]->*(sent)
        RETURN start, end, type
            , COLLECT(DISTINCT start_name) AS start_names
            , COLLECT(DISTINCT end_name) AS end_names
            , start_intv
            , end_intv
        """
    if do_print:
        print(q)  # noqa: T201

    res = db.cypher_query(
        q,
        params={"uid": uid},
        resolve_objects=True,
    )

    g = nx.MultiDiGraph()
    uids = {}
    defs = []

    def add_proc(node: str, name_nodes: list[list], intv: Any | None = None):
        if node not in uids:
            names = [n.val for n in name_nodes[0]]
            if names:
                defs.append(Def.create(node, names))
            if intv is not None:
                EdgeType.WHEN.add_edge(g, node, intv.val)

    for row in res[0]:
        (
            start,
            end,
            type_,
            start_names,
            end_names,
            start_intv,
            end_intv,
        ) = row
        t: EdgeType = getattr(EdgeType, type_)
        t.add_edge(g, start.val, end.val)
        # add_def(start.val)
        add_proc(start.val, start_names, start_intv)
        add_proc(end.val, end_names, end_intv)
        uids[start.val] = start.uid
        uids[end.val] = end.uid
    mdefs, stddefs, _ = MergedDef.create_and_parted(defs)
    [md.add_edge(g) for md in mdefs]
    [d.add_edge(g) for d in stddefs]
    return KnowdeDetail(uid=uid, g=g, uids=uids)
