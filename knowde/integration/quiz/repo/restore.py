"""復元."""

from collections.abc import Iterable

import networkx as nx
from neo4j.graph import Path as NeoPath
from neomodel import adb

from knowde.feature.knowde.repo.detail import fetch_knowdes_with_detail
from knowde.integration.quiz.domain.domain import (
    QuizSource,
    QuizSourceContainer,
    QuizType,
)
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.types import UUIDy, to_uuid


def graph_neo4j2nx(paths: Iterable[NeoPath]) -> nx.MultiDiGraph:
    """neo4jをnxに変換."""
    g = nx.MultiDiGraph()
    for p in paths:
        for rel in p.relationships:
            s = rel.start_node.get("uid") if rel.start_node else None
            e = rel.end_node.get("uid") if rel.end_node else None
            t = EdgeType[rel.type]
            g.add_edge(s, e, type=t)
    return g


async def restore_quiz_sources(
    quiz_ids: Iterable[UUIDy],
) -> list[QuizSource]:
    """クイズの復元."""
    q = """
        UNWIND $quiz_ids AS quiz_id
        MATCH (quiz: Quiz {uid: quiz_id})
        OPTIONAL MATCH (quiz)-[:QUIZ_TARGET]->(tgt)
        OPTIONAL MATCH (quiz)-[:QUIZ_OPTION]->(opt)
        OPTIONAL MATCH p = SHORTEST 1 (tgt)-[:!QUIZ_OPTION|QUIZ_TARGET]-*(opt)
        RETURN
            quiz
            , tgt.uid
            , COLLECT(opt.uid) AS options
            , COLLECT(p) AS paths
    """
    uids = [to_uuid(uid).hex for uid in quiz_ids]
    rows, _ = await adb.cypher_query(q, params={"quiz_ids": uids})

    containers: list[QuizSourceContainer] = []
    for row in rows:
        quiz, tgt_uid, opt_uids, paths = row
        case = QuizSourceContainer(
            quiz_id=quiz.get("uid"),
            statement_type=QuizType[quiz.get("statement_type")],
            target_id=tgt_uid,
            source_ids=set(opt_uids),
            g=graph_neo4j2nx(paths),
        )
        containers.append(case)
    uids = QuizSourceContainer.concat_uids_for_batch_fetch(containers)
    kns = await fetch_knowdes_with_detail(uids)
    return [c.to_source(kns) for c in containers]
    # for sid in c.source_ids:
    #     tgt = kns[c.target_id]
    #     src = kns[sid]
    #     print(
    #         f"{src} -> {tgt}",
    #         QuizRel.of(*path2edgetypes(c.g, sid, c.target_id)),
    #     )
