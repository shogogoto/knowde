"""候補から選択肢を選ぶ."""


# # 詳細や結論などの特定の関係内から探す
# # scoreでソートできたほうが良い
# async def list_candidates_by_rel_type(target_sent_id: UUIDy):
#     pass

from uuid import UUID

from knowde.integration.quiz.errors import SamplingError
from knowde.integration.quiz.repo.select_option.candidate import (
    list_candidates_by_radius,
)
from knowde.integration.quiz.repo.select_option.sample import sample_options_randomly
from knowde.shared.types import UUIDy


async def retry_select_random_options(
    target_sent_uid: UUIDy,
    radius: int,
    n_option: int,  # 選択肢の数
    n_retry: int = 5,  # 失敗時に半径をインクリして繰り返す回数
    has_term: bool = False,  # noqa: FBT001, FBT002
) -> list[UUID]:
    """対象の指定半径からランダムに選ぶ.候補不足時は半径を広げてリトライする."""
    r = radius
    last_n_cand = -1  # 0以上だと初回でループが終了してしまう可能性
    attempt = 0
    for attempt in range(1, n_retry + 1):  # noqa: B007
        cand_uids = await list_candidates_by_radius(
            target_sent_uid,
            r,
            has_term,
        )
        current_n_cand = len(cand_uids)
        # 半径を増やしても候補が増えないならretryしても無駄
        if last_n_cand == current_n_cand:
            break
        last_n_cand = len(cand_uids)
        try:
            return sample_options_randomly(cand_uids, n_option=n_option)
        except SamplingError:
            r += 1
            continue
    msg = (
        f"指定数だけの選択肢を取得できなかった: "
        f"試行回数={attempt}/{n_retry}"
        f", 最終半径={radius}->{r}"
        f", 最終候補数={last_n_cand}"
    )
    raise SamplingError(msg)


# A| random -> top : ランダムな候補の中から上位を選ぶ
# B| top -> random : 上位の候補の中からランダムに選ぶ
# で結果が違う
# Aの方が幅広いため難易度高い
async def select_options_top_score(
    target_sent_uid: UUIDy,
    radius: int | None = None,
    n_option: int | None = None,  # 選択肢の数 Noneでは
    has_term: bool = False,  # noqa: FBT001, FBT002
):
    """スコア上位の順に選ぶ."""
