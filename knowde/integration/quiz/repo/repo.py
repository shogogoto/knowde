"""quiz repo."""

import random
from collections.abc import Iterable
from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

import networkx as nx
from more_itertools import flatten
from neomodel import adb
from pydantic import Field, TypeAdapter

from knowde.feature.knowde.repo.detail import fetch_knowdes_with_detail
from knowde.integration.quiz.domain.domain import (
    QuizSource,
    QuizSourceIdCase,
    QuizStatementType,
)
from knowde.integration.quiz.repo.select_option.distract import (
    list_candidates_by_radius,
    list_candidates_in_resource,
)
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.types import UUIDy, to_uuid
from knowde.shared.util import TZ

type NOption = Annotated[int, Field(gt=2, title="選択肢の数")]
nopt_adapter = TypeAdapter(NOption)


async def create_term2sent_quiz(
    target_sent_uid: UUIDy,
    radius: int | None = None,
    n_option: int = 4,  # 選択肢の数
    now: datetime = datetime.now(tz=TZ),
) -> UUID:
    """単文当てクイズの永続化."""
    uids = await list_candidates_by_radius(target_sent_uid, radius=2)
    quiz_uid = uuid4()
    q = """
        MATCH (tgt: Sentence {uid: $target_uid})
        CREATE (quiz: Quiz {
            uid: $quiz_uid
            , statement_type: $statement_type
            , is_link_broken: false
            , created: datetime($now)
        })-[:QUIZ_TARGET]->(tgt)
        WITH quiz
        UNWIND $dist_uids AS duid
        MATCH (dst: Sentence {uid: duid})
        CREATE (quiz)-[:QUIZ_OPTION]->(dst)
        RETURN quiz
            , COLLECt(dst) AS distractors
    """
    # targetがoptionになる分を引く
    n_sample = nopt_adapter.validate_python(n_option) - 1
    uids = (
        await list_candidates_in_resource(target_sent_uid)
        if radius is None
        else await list_candidates_by_radius(target_sent_uid, radius)
    )
    opt_uids = [to_uuid(uid) for uid in random.sample(uids, n_sample)]
    _rows, _ = await adb.cypher_query(
        q,
        params={
            "quiz_uid": quiz_uid.hex,
            "target_uid": to_uuid(target_sent_uid).hex,
            "dist_uids": [u.hex for u in opt_uids],
            "statement_type": QuizStatementType.TERM2SENT.name,
            "now": now.isoformat(),
        },
    )
    return quiz_uid


async def restore_quiz(quiz_ids: Iterable[UUIDy]) -> QuizSource:  # noqa: PLR0914
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
    rows, _ = await adb.cypher_query(
        q,
        params={"quiz_ids": uids},
    )

    cases = []
    g = nx.MultiDiGraph()
    for row in rows:
        quiz, tgt_uid, opt_uids, paths = row
        case = QuizSourceIdCase(
            quiz_id=quiz.get("uid"),
            statement_type=QuizStatementType[quiz.get("statement_type")],
            target_id=tgt_uid,
            source_ids=set(opt_uids),
        )
        cases.append(case)
        for p in paths:
            for rel in p.relationships:
                s = rel.start_node.get("uid") if rel.start_node is not None else None
                e = rel.end_node.get("uid") if rel.end_node is not None else None
                t = EdgeType[rel.type]
                g.add_edge(s, e, type=t)
    # 一括でfetchを完了させる
    uids_for_fetch = set(flatten([[c.target_id, *c.source_ids] for c in cases]))
    _kns = await fetch_knowdes_with_detail(uids_for_fetch)

    # rg = nx.relabel_nodes(g, kns)
    # nxprint(rg, True)
    # print("-" * 30)
    # for c in cases:
    #     for sid in c.source_ids:
    #         tgt = kns[c.target_id]
    #         src = kns[sid]
    #         print(f"src -> tgt = {src} = {tgt}")
    #         a = path2edgetypes(g, c.target_id, sid)
