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

import pytest

from knowde.integration.quiz.errors import SamplingError

from .domain import head_sample_safe, random_sample_safe


def test_sample_safe():
    """候補が足りないときに選択肢数を候補数に合わせる."""
    cands = list(range(5))
    samples = random_sample_safe(cands, n_sample=4)
    assert len(samples) == 4  # noqa: PLR2004
    with pytest.raises(SamplingError):
        random_sample_safe(cands, n_sample=100)  # 候補より選択肢多い
    with pytest.raises(SamplingError):
        head_sample_safe(cands, n_sample=100)  # 候補より選択肢多い

    samples = head_sample_safe(cands, n_sample=4)
    assert len(samples) == 4  # noqa: PLR2004
