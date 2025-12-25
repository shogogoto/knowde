"""候補からランダムに抽出するロジック.

ロジックだからdomainに書くべきかもと思ったが、
DBから候補を絞る際に使うのでここに書く
"""

import random
from collections.abc import Sequence
from uuid import UUID

from knowde.integration.quiz.errors import OutOfRangeSampleError
from knowde.shared.types import UUIDy, to_uuid


def sample_options_ramdomly(
    candidate_uids: Sequence[UUIDy],
    n_option: int,  # 選択肢の数 Noneでは
) -> list[UUID]:
    """対象の指定半径からランダムに選ぶ."""
    if n_option < 2:  # noqa: PLR2004
        msg = f"選択肢の数は2以上: {n_option}"
        raise OutOfRangeSampleError(msg)
    n_sample = n_option - 1  # target分を引く
    if n_sample > len(candidate_uids):
        msg = f"選択肢数が候補数より大きい: {n_sample} > {len(candidate_uids)}"
        raise OutOfRangeSampleError(msg)
    return [to_uuid(uid) for uid in random.sample(candidate_uids, n_sample)]
