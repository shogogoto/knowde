"""候補から選択肢を選ぶ."""


# # 詳細や結論などの特定の関係内から探す
# # scoreでソートできたほうが良い
# async def list_candidates_by_rel_type(target_sent_id: UUIDy):
#     pass

import random
from typing import Annotated
from uuid import UUID

from pydantic import Field, TypeAdapter

from knowde.integration.quiz.repo.select_option.candidate import (
    list_candidates_by_radius,
)
from knowde.shared.types import UUIDy, to_uuid

type NOption = Annotated[int, Field(gt=2, title="選択肢の数")]
nopt_adapter = TypeAdapter(NOption)


async def select_random_options(
    target_sent_uid: UUIDy,
    radius: int | None = None,
    n_option: int = 4,  # 選択肢の数
) -> list[UUID]:
    """対象の指定半径からランダムに選ぶ."""
    n_sample = nopt_adapter.validate_python(n_option) - 1  # target分を引く
    uids = await list_candidates_by_radius(target_sent_uid, radius)
    return [to_uuid(uid) for uid in random.sample(uids, n_sample)]
