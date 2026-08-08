"""復元."""

from collections.abc import Iterable
from typing import Final

import networkx as nx
from neomodel import adb

from tanbun.feature.domain.graph.edge_type import EdgeType
from tanbun.feature.domain.types import UUIDy, to_uuid
from tanbun.feature.quiz.domain.domain import QuizSource
from tanbun.feature.quiz.domain.parts import (
    QuizOption,
    QuizRel,
    QuizType,
)
from tanbun.feature.quiz.domain.rel import QUIZ_REL_EDGE_TYPES
from tanbun.feature.quiz.errors import QuizRestoreError
from tanbun.feature.repo.graph import neo4jpath2nx
from tanbun.feature.tanbun.domain import Tanbun
from tanbun.feature.tanbun.repo.detail import fetch_tanbuns_with_detail

KNOWLEDGE_REL_TYPES: Final = "|".join(
    edge_type.name for edge_type in QUIZ_REL_EDGE_TYPES
)


def nx2options(
    uids: Iterable[str],
    *,
    correct_ids: Iterable[str],
    target_id: str,
    g: nx.DiGraph,
    uid2kn: dict[str, Tanbun],
    quiz_type: QuizType,
) -> dict[str, QuizOption]:
    """nxをoptionsに変換."""
    options = {}
    correct_id_set = set(correct_ids)
    for uid in uids:
        try:
            rels = QuizRel.of(*EdgeType.path2edgetypes(g, target_id, uid))
        except (nx.NetworkXNoPath, nx.NodeNotFound) as error:
            requires_path = quiz_type is QuizType.PAIR2REL or (
                quiz_type is QuizType.REL2PAIR and uid in correct_id_set
            )
            if requires_path:
                msg = f"{quiz_type}の知識pathが見つかりません: {target_id} -> {uid}"
                raise QuizRestoreError(msg) from error
            rels = None
        options[uid] = QuizOption(
            val=uid2kn[uid].sentence_or_def,
            rels=rels,
        )
    return options


async def restore_quiz_sources(
    quiz_ids: Iterable[UUIDy],
) -> list[QuizSource]:
    """クイズの復元."""
    sources, _ = await restore_quiz_sources_with_tanbuns(quiz_ids)
    return sources


async def restore_quiz_sources_with_tanbuns(
    quiz_ids: Iterable[UUIDy],
    extra_uids: Iterable[UUIDy] = (),
) -> tuple[list[QuizSource], dict[str, Tanbun]]:
    """クイズと、その復元に使ったTanbunをまとめて返す."""
    q = """
        UNWIND $quiz_ids AS quiz_id
        MATCH (quiz: Quiz {uid: quiz_id})
        OPTIONAL MATCH (quiz)-[:QUIZ_TARGET]->(tgt)
        OPTIONAL MATCH (quiz)-[:QUIZ_OPTION]->(opt)
        OPTIONAL MATCH (quiz)-[:CORRECT]->(crct)
        WITH quiz, tgt, crct
            , [opt, crct] AS srcs
        UNWIND srcs AS src
        OPTIONAL MATCH p = SHORTEST 1 (tgt)-[:__KNOWLEDGE_REL_TYPES__]-*(src)
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
    q = q.replace("__KNOWLEDGE_REL_TYPES__", KNOWLEDGE_REL_TYPES)
    qids = [to_uuid(uid).hex for uid in quiz_ids]
    rows, _ = await adb.cypher_query(q, params={"quiz_ids": qids})
    flat = [row[0] for row in rows]
    all_uids = set().union(
        *(r["source_ids"] for r in flat),
        (to_uuid(uid).hex for uid in extra_uids),
    )
    kns = await fetch_tanbuns_with_detail(all_uids)
    sources = []
    for r in flat:
        quiz_type = QuizType[r["quiz_type"]]
        sources.append(
            QuizSource(
                quiz_id=r["quiz_id"],
                quiz_type=quiz_type,
                target_id=r["target_id"],
                correct_ids=r["correct_ids"],
                sources=nx2options(
                    r["source_ids"],
                    correct_ids=r["correct_ids"],
                    target_id=r["target_id"],
                    g=neo4jpath2nx(r["paths"]),
                    uid2kn=kns,
                    quiz_type=quiz_type,
                ),
                created=r["created"],
                no_correct_option=r["quiz"].get("no_correct_option"),
            ),
        )
    return sources, kns
