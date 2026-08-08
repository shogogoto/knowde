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

from random import Random

import pytest

from tanbun.feature.quiz.domain.rel import QuizRel
from tanbun.feature.quiz.errors import SamplingError

from .domain import random_sample_safe, rank_distinct_paths


def test_sample_safe():
    """候補が足りないときに選択肢数を候補数に合わせる."""
    samples = random_sample_safe(range(5), n_sample=4)
    assert len(samples) == 4  # noqa: PLR2004
    with pytest.raises(SamplingError):
        random_sample_safe(range(5), n_sample=100)  # 候補より選択肢多い

    # with pytest.raises(SamplingError):
    #     head_sample_safe(cands, n_sample=100)  # 候補より選択肢多い
    # samples = head_sample_safe(cands, n_sample=4)
    # assert len(samples) == 4


def test_rank_distinct_paths():
    """同じ表示を除外し、正解pathに近い実在pathから並べる."""
    correct = [QuizRel.PREMISE, QuizRel.DETAIL]
    candidates = {
        "same-as-correct": [QuizRel.PREMISE, QuizRel.DETAIL],
        "same-length": [QuizRel.CONCLUSION, QuizRel.EXAMPLE],
        "same-position": [QuizRel.PREMISE, QuizRel.EXAMPLE],
        "duplicate-a": [QuizRel.REFER],
        "duplicate-b": [QuizRel.REFER],
        "far": [QuizRel.PEER, QuizRel.PEER, QuizRel.PEER, QuizRel.PEER],
    }

    ranked = rank_distinct_paths(correct, candidates, rng=Random(0))  # noqa: S311

    assert ranked[:2] == ["same-position", "same-length"]
    assert "same-as-correct" not in ranked
    assert len({"duplicate-a", "duplicate-b"} & set(ranked)) == 1
