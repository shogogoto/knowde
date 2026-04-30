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
        OPTIONAL MATCH (quiz)-[:CORRECT]->(crct)
        WITH quiz, tgt, crct
            , [opt, crct] AS srcs
        UNWIND srcs AS src
        OPTIONAL MATCH p = SHORTEST 1 (tgt)
            -[:!QUIZ_OPTION|QUIZ_TARGET]-*(src)
        RETURN
            quiz
            , tgt.uid
            , COLLECT(src.uid) AS options
            , COLLECT(p) AS paths
            , COLLECT(crct.uid) AS corrects

    """
    uids = [to_uuid(uid).hex for uid in quiz_ids]
    rows, _ = await adb.cypher_query(q, params={"quiz_ids": uids})

    containers: list[QuizSourceContainer] = []
    for row in rows:
        quiz, tgt_uid, opt_uids, paths, crct_uids = row
        crct_uids = set(crct_uids)
        case = QuizSourceContainer(
            quiz_id=quiz.get("uid"),
            quiz_type=QuizType[quiz.get("quiz_type")],
            target_id=tgt_uid,
            correct_ids=crct_uids,
            source_ids=set(opt_uids).union(crct_uids),
            g=graph_neo4j2nx(paths),
            created=quiz.get("created"),
        )
        containers.append(case)
    uids = QuizSourceContainer.concat_uids_for_batch_fetch(containers)
    kns = await fetch_knowdes_with_detail(uids)
    return [c.to_source(kns) for c in containers]
