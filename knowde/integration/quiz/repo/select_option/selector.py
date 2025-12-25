"""候補から選択肢を選ぶ."""


# # 詳細や結論などの特定の関係内から探す
# # scoreでソートできたほうが良い
# async def list_candidates_by_rel_type(target_sent_id: UUIDy):
#     pass

from uuid import UUID

from knowde.integration.quiz.repo.select_option.candidate import (
    list_candidates_by_radius,
)
from knowde.integration.quiz.repo.select_option.sample import sample_options_ramdomly
from knowde.shared.types import UUIDy


async def select_random_options(
    target_sent_uid: UUIDy,
    radius: int | None = None,
    n_option: int = 4,  # 選択肢の数
    has_term: bool = False,  # noqa: FBT001, FBT002
) -> list[UUID]:
    """対象の指定半径からランダムに選ぶ."""
    cand_uids = await list_candidates_by_radius(target_sent_uid, radius, has_term)
    return sample_options_ramdomly(cand_uids, n_option=n_option)


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
