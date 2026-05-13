"""復元."""

import operator
from collections.abc import Iterable
from functools import reduce
from typing import Any, NamedTuple, Self
from uuid import UUID

import networkx as nx
from neo4j.graph import Path as NeoPath
from neomodel import adb

from knowde.feature.knowde import Knowde
from knowde.feature.knowde.repo.detail import fetch_knowdes_with_detail
from knowde.integration.quiz.domain.domain import (
    QuizSource,
)
from knowde.integration.quiz.domain.parts import (
    QuizOption,
    QuizRel,
    QuizType,
    path2edgetypes,
)
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.types import NXGraph, UUIDy, to_uuid
from knowde.shared.util import Neo4jDateTime


def neo4jpath2nx(paths: Iterable[NeoPath]) -> nx.MultiDiGraph:
    """neo4jをnxに変換."""
    g = nx.MultiDiGraph()
    for p in paths:
        for rel in p.relationships:
            s = rel.start_node.get("uid") if rel.start_node else None
            e = rel.end_node.get("uid") if rel.end_node else None
            t = EdgeType[rel.type]
            g.add_edge(s, e, type=t)
    return g


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
            rels=QuizRel.of(*path2edgetypes(g, target_id, uid)),
        )
        for uid in uids
    }


class QuizTmpRaw(NamedTuple):
    """一時的なquizの容れ物."""

    quiz_id: UUID
    quiz_type: QuizType
    target_id: str
    correct_ids: set[str]
    source_ids: set[str]
    g: NXGraph  # EdgeType-QuizRel用
    created: Neo4jDateTime

    @classmethod
    def create(cls, row: Any) -> Self:
        """変換."""
        quiz, tgt_uid, opt_uids, paths, correct_uids = row
        quiz_id, qt, created = operator.itemgetter("uid", "quiz_type", "created")(quiz)
        g = neo4jpath2nx(paths)
        correct_uids = set(correct_uids)
        source_ids = set(opt_uids).union(correct_uids).union({tgt_uid})
        return cls(
            quiz_id=quiz_id,
            quiz_type=QuizType[qt],
            target_id=tgt_uid,
            correct_ids=correct_uids,
            source_ids=source_ids,
            g=g,
            created=created,
        )


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
    qids = [to_uuid(uid).hex for uid in quiz_ids]
    rows, _ = await adb.cypher_query(q, params={"quiz_ids": qids})
    data = [QuizTmpRaw.create(row) for row in rows]
    all_uids = reduce(operator.or_, (c.source_ids for c in data), set())
    kns = await fetch_knowdes_with_detail(all_uids)
    return [
        QuizSource(
            quiz_id=d.quiz_id,
            quiz_type=d.quiz_type,
            target_id=d.target_id,
            correct_ids=list(d.correct_ids),
            sources=nx2options(d.source_ids, d.target_id, d.g, kns),
            created=d.created,
        )
        for d in data
    ]
