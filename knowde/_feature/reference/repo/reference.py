from __future__ import annotations

from operator import attrgetter, itemgetter
from uuid import UUID  # noqa: TCH003

import networkx as nx

from knowde._feature._shared.repo.query import query_cypher
from knowde._feature.reference.domain import (
    Chapter,
    ReferenceGraph,
    ReferenceTree,
    Section,
)
from knowde._feature.reference.repo.label import refroot_type, to_refmodel


def find_reftree(ref_uid: UUID) -> ReferenceTree:
    res = query_cypher(
        """
        MATCH (r:Reference {uid: $uid})
        // Chapterが親を1つだけ持つneomodel制約Oneのためのedgeの向き
        OPTIONAL MATCH (r)<-[crel:COMPOSE]-(c:Chapter)
        OPTIONAL MATCH (c)<-[srel:COMPOSE]-(:Section)
        RETURN
            r,
            crel,
            collect(srel) as srels
        """,
        params={"uid": ref_uid.hex},
    )

    ref = res.get("r", convert=to_refmodel)[0]
    t = res.get("r", convert=refroot_type)[0]

    chaps = {}
    for chap_rel, sec_rels in zip(
        res.get("crel"),
        res.get("srels", row_convert=itemgetter(0)),
    ):
        if chap_rel is None:
            continue
        sorted_sec_rels = sorted(sec_rels, key=attrgetter("order"))
        secs = [Section.to_model(rel.start_node()) for rel in sorted_sec_rels]
        chap = Chapter.to_model(chap_rel.start_node())
        chaps[chap_rel.order] = chap.with_sections(secs)
    return ReferenceTree(
        root=ref,
        chapters=[chaps[i] for i in sorted(chaps.keys())],
        reftype=t,
    )


def find_reftree2(ref_uid: UUID) -> ReferenceGraph:
    """ChapterやSectionのuidであってもTreeを返す."""
    res = query_cypher(
        """
        MATCH (tgt:Reference {uid: $uid})
        // Chapterが親を1つだけ持つneomodel制約Oneのためのedgeの向き
        OPTIONAL MATCH (tgt)-[rel:COMPOSE]-*(:Reference)
        UNWIND rel as rels_
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
