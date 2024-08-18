from __future__ import annotations

from operator import itemgetter
from uuid import UUID  # noqa: TCH003

import networkx as nx

from knowde._feature.reference.domain import (
    ReferenceGraph,
    ReferenceTree,
)
from knowde._feature.reference.repo.label import to_refmodel
from knowde.core.repo.query import query_cypher


def find_reftree(ref_uid: UUID) -> ReferenceTree:
    return find_refgraph(ref_uid).to_tree()


def find_refgraph(ref_uid: UUID) -> ReferenceGraph:
    """ChapterやSectionのuidであってもTreeを返す."""
    res = query_cypher(
        """
        MATCH (tgt:Reference {uid: $uid})
        OPTIONAL MATCH (tgt)-[rel:COMPOSE]-*(:Reference)
        UNWIND
            CASE
                WHEN rel = [] THEN [null]
                ELSE rel
            END as rels_
        RETURN
            tgt,
            collect(DISTINCT rels_) as rels
        """,
        params={"uid": ref_uid.hex},
    )
    ref = res.get("tgt", convert=to_refmodel)[0]
    g = nx.DiGraph()
    for rel in res.get("rels", row_convert=itemgetter(0))[0]:
        child = to_refmodel(rel.start_node())
        parent = to_refmodel(rel.end_node())
        g.add_edge(parent, child, order=rel.order)  # DB上の向きと逆
    return ReferenceGraph(target=ref, g=g)


def remove_ref(ref_uid: UUID) -> None:
    """本配下を削除."""
    query_cypher(
        """
        MATCH (tgt:Reference {uid: $uid})
        OPTIONAL MATCH (tgt)<-[:COMPOSE]-(c:Chapter)
        OPTIONAL MATCH (c)<-[:COMPOSE]-(s:Section)
        DETACH DELETE tgt, c, s
        """,
        params={"uid": ref_uid.hex},
    )
