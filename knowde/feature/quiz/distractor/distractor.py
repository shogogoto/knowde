"""誤答肢repo."""

import random
from uuid import UUID

import networkx as nx
from neomodel import adb

from knowde.feature.domain.graph.edge_type import EdgeType
from knowde.feature.domain.types import UUIDy, to_uuid
from knowde.feature.quiz.candidate.types import CandidateType
from knowde.feature.quiz.distractor.domain import (
    random_sample_safe,
    rank_distinct_paths,
)
from knowde.feature.quiz.domain.rel import QuizRel
from knowde.feature.quiz.errors import (
    InsufficientOptionsError,
    SamplingError,
)
from knowde.feature.quiz.repo.restore import KNOWLEDGE_REL_TYPES
from knowde.feature.repo.graph import neo4jpath2nx

MAX_RELATION_PATH_CANDIDATES = 50
MAX_RELATION_PATH_DEPTH = 3


# correct == target の場合
async def fetch_distractor_ids(
    sent_ids: list[UUIDy],
    ct: CandidateType,
    n_distractor: int,
    must_has_term: bool,  # noqa: FBT001
    exclude_sent_ids: list[UUIDy] | None = None,
) -> list[UUID]:
    """誤答肢を取得する."""
    cand_uids = await ct.fetch(
        sent_ids,
        must_has_term=must_has_term,
        exclude_sent_ids=exclude_sent_ids,
    )
    if set(exclude_sent_ids or []) & set(cand_uids):
        msg = "誤答肢に含まれる単文は除外する"
        raise ValueError(msg)

    try:
        return random_sample_safe(cand_uids, n_sample=n_distractor)
    except SamplingError as error:
        msg = f"誤答肢が不足しています: 必要数={n_distractor}, 候補数={len(cand_uids)}"
        raise InsufficientOptionsError(msg) from error


async def _fetch_relation_paths(
    target_id: UUIDy,
    candidate_ids: list[UUIDy],
) -> dict[UUID, list[QuizRel]]:
    """対象Sentenceから各候補までの最短knowledge pathを取得."""
    query = """
        MATCH (target: Sentence {uid: $target_id})
        UNWIND $candidate_ids AS candidate_id
        MATCH (candidate: Sentence {uid: candidate_id})
        MATCH path = SHORTEST 1
            (target)-[:__KNOWLEDGE_REL_TYPES__]-{1, __MAX_PATH_DEPTH__}(candidate)
        RETURN candidate.uid, path
    """
    query = query.replace("__KNOWLEDGE_REL_TYPES__", KNOWLEDGE_REL_TYPES)
    query = query.replace("__MAX_PATH_DEPTH__", str(MAX_RELATION_PATH_DEPTH))
    rows, _ = await adb.cypher_query(
        query,
        params={
            "target_id": to_uuid(target_id).hex,
            "candidate_ids": [to_uuid(uid).hex for uid in candidate_ids],
        },
    )
    target_uid = to_uuid(target_id).hex
    paths = {}
    for candidate_id, path in rows:
        try:
            paths[to_uuid(candidate_id)] = QuizRel.of(
                *EdgeType.path2edgetypes(
                    neo4jpath2nx([path]),
                    target_uid,
                    candidate_id,
                ),
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            continue
    return paths


async def fetch_pair2rel_distractor_ids(
    target_id: UUIDy,
    candidate_type: CandidateType,
    n_distractor: int,
    correct_ids: list[UUIDy],
    rng: random.Random | None = None,
) -> list[UUID]:
    """実在pathから正解に近く、表示が重複しないPAIR2REL誤答肢を選ぶ."""
    if not correct_ids:
        msg = "PAIR2RELには正解Sentenceが必要"
        raise InsufficientOptionsError(msg)

    candidate_ids = await candidate_type.fetch(
        [target_id],
        exclude_sent_ids=correct_ids,
    )
    # ALLはリソース内の全単文を返すため、そのまま最短pathを探索すると
    # 大きいresourceでrecommendation APIがタイムアウトする。
    candidate_ids = candidate_ids[:MAX_RELATION_PATH_CANDIDATES]
    paths = await _fetch_relation_paths(
        target_id,
        [*correct_ids, *candidate_ids],
    )
    correct_path = paths.get(to_uuid(correct_ids[0]))
    if correct_path is None:
        msg = "PAIR2RELの正解pathが見つからない"
        raise InsufficientOptionsError(msg)

    candidate_paths = {
        candidate_id: paths[candidate_id]
        for candidate_id in map(to_uuid, candidate_ids)
        if candidate_id in paths
    }
    selected = rank_distinct_paths(
        correct_path,
        candidate_paths,
        rng=rng,
    )[:n_distractor]
    if len(selected) != n_distractor:
        msg = (
            f"表示が異なるPAIR2REL誤答肢が指定数{n_distractor}に"
            f"一致しない: {len(selected)}"
        )
        raise InsufficientOptionsError(msg)
    return selected
