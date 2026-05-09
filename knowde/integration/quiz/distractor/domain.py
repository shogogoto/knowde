"""誤答肢作成domain."""

import random
from collections.abc import Sequence
from enum import StrEnum, auto
from uuid import UUID

from knowde.integration.quiz.errors import SamplingError
from knowde.shared.types import UUIDy, to_uuid


class SamplingType(StrEnum):
    """選択肢選定ロジックの種類."""

    RANDOM = auto()
    CLOSER = auto()  # 近い順に選ぶ
    TOP_SCORE = auto()


def sample_safe(
    candidate_uids: Sequence[UUIDy],
    n_option: int,  # 選択肢の数 Noneでは
) -> list[UUID]:
    """選択肢数だけ選ぶのを保証する."""
    if len(candidate_uids) != len(set(candidate_uids)):
        msg = f"選択肢候補が重複している: {candidate_uids}"
        raise SamplingError(msg)
    if n_option < 2:  # noqa: PLR2004
        msg = f"選択肢の数は2以上必要 (入力: {n_option})"
        raise SamplingError(msg)
    n_sample = n_option - 1  # target分を引く
    if n_sample > len(candidate_uids):
        msg = (
            f"選択肢候補が足りない (指定数: {n_sample}, 候補数: {len(candidate_uids)})"
        )
        raise SamplingError(msg)
    return [to_uuid(uid) for uid in random.sample(candidate_uids, n_sample)]


# # 詳細や結論などの特定の関係内から探す
# # scoreでソートできたほうが良い
# async def list_candidates_by_rel_type(target_sent_id: UUIDy):
#     pass


# 引数をbindした関数
# その内の１つのパラメータを指定し、それを+1してリトライ
# async def retry_sample_incr(
#     target_sent_uid: UUIDy,
#     radius: int,
#     n_option: int,  # 選択肢の数
#     n_retry: int = 5,  # 失敗時に半径をインクリして繰り返す回数
#     has_term: bool = False,
# ) -> list[UUID]:
#     """条件を緩めながら一定の候補数になるまで取得を試す."""
#     r = radius
#     last_n_cand = -1  # 0以上だと初回でループが終了してしまう可能性
#     attempt = 0
#     for attempt in range(1, n_retry + 1):
#         cand_uids = await list_candidates_by_radius(
#             target_sent_uid,
#             r,
#             has_term,
#         )
#         current_n_cand = len(cand_uids)
#         # 半径を増やしても候補が増えないならretryしても無駄
#         if last_n_cand == current_n_cand:
#             break
#         last_n_cand = len(cand_uids)
#         try:
#             return sample_safe(cand_uids, n_option=n_option)
#         except SamplingError:
#             r += 1
#             continue
#     msg = (
#         f"指定数だけの選択肢を取得できなかった: "
#         f"試行回数={attempt}/{n_retry}"
#         f", 最終半径={radius}->{r}"
#         f", 最終候補数={last_n_cand}"
#     )
#     raise SamplingError(msg)
