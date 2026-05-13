"""復元."""

from collections.abc import Iterable

import networkx as nx
from neomodel import adb

from knowde.feature.knowde import Knowde
from knowde.feature.knowde.repo.detail import fetch_knowdes_with_detail
from knowde.integration.quiz.domain.domain import QuizSource
from knowde.integration.quiz.domain.parts import (
    QuizOption,
    QuizRel,
    QuizType,
)
from knowde.shared.nxutil.db import neo4jpath2nx
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.types import UUIDy, to_uuid


def nx2options(
    uids: Iterable[str],
    target_id: str,
    g: nx.DiGraph,
    uid2kn: dict[str, Knowde],
) -> dict[str, QuizOption]:
    """nxをoptionsに変換."""
    return {
        uid: QuizOption(
            val=uid2kn[uid].sentence_or_def,
            rels=QuizRel.of(*EdgeType.path2edgetypes(g, target_id, uid)),
        )
        for uid in uids
    }


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
        WITH
            quiz
            , tgt.uid AS target_id
            , COLLECT(src.uid) AS option_ids
            , COLLECT(p) AS paths
            , COLLECT(DISTINCT crct.uid) AS correct_ids
        RETURN {
            quiz: quiz
            , quiz_id: quiz.uid
            , quiz_type: quiz.quiz_type
            , created: quiz.created
            , target_id: target_id
            , correct_ids: correct_ids
            , option_ids: option_ids
            , paths: paths
            , source_ids: option_ids + correct_ids + [target_id]
            }

    """
    qids = [to_uuid(uid).hex for uid in quiz_ids]
    rows, _ = await adb.cypher_query(q, params={"quiz_ids": qids})
    flat = [row[0] for row in rows]
    all_uids = set().union(*(r["source_ids"] for r in flat))
    kns = await fetch_knowdes_with_detail(all_uids)
    return [
        QuizSource(
            quiz_id=r["quiz_id"],
            quiz_type=QuizType[r["quiz_type"]],
            target_id=r["target_id"],
            correct_ids=r["correct_ids"],
            sources=nx2options(
                r["source_ids"],
                r["target_id"],
                neo4jpath2nx(r["paths"]),
                kns,
            ),
            created=r["created"],
        )
        for r in flat
    ]
