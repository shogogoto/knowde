"""ランダムに選ぶロジックテスト.

候補が足りなかった場合にエラーになる.
候補0の場合はエラー 2択までは意味ある

n_cand < n_option 候補足りなくて指定した数の選択肢を取れない
    -> 候補数と同じ指定数に減らして調整

    -> 候補を取り直す
        n_cand >= n_option となるまで半径をインクリして候補取得を繰り返す
        予め候補idと距離を返すようにしとけばfetch回数を減らせそうだが問題になったら対応

ok n_cand = n_option
ok n_cand > n_option
"""

from uuid import uuid4

import pytest

from knowde.integration.quiz.errors import SamplingError

from . import sample_options_randomly


def test_out_of_range_sample_error():
    """候補が足りないときに選択肢数を候補数に合わせる."""
    with pytest.raises(SamplingError):  # 候補1は無意味
        sample_options_randomly([], n_option=1)
    cand_uids = [uuid4() for _ in range(5)]
    with pytest.raises(SamplingError):
        sample_options_randomly(cand_uids, n_option=1)  # 選択肢数足りない
    sample_options_randomly(cand_uids, n_option=2)

    with pytest.raises(SamplingError):
        sample_options_randomly(cand_uids, n_option=100)  # 候補より選択肢多い
