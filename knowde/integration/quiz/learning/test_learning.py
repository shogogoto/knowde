"""test learning.

クイズ管理
  □ バッチ作成
  □ 正答率集計
  □ coverage算出
  □ クイズ提案.
"""

from random import Random

import pytest

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.namespace import fetch_namespace
from knowde.feature.knowde.repo.detail import fetch_knowdes_with_detail
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.domain import (
    QuizCoverage,
    QuizTargetOrder,
    QuizTargetPool,
)
from knowde.integration.quiz.learning.repo import (
    fetch_coverage,
    fetch_covered_sent_ids,
    fetch_sort_by_score,
    fetch_target_ids,
    fetch_uncovered_sent_ids,
)
from knowde.integration.quiz.repo.create import generate_quiz
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser
from knowde.shared.user.testing import aregister

from .fixture import fx_learning

u = async_fixture()(fx_learning)


@mark_async_test()
async def test_fetch_coverage(u: LUser):
    """リソース内のクイズ化済み単文の割合を取得."""
    ns = await fetch_namespace(u.uid)
    rid = ns.resources[0].uid
    aaa = LSentence.nodes.first(val="a")

    expected = QuizCoverage(
        resource_id=rid,
        user_id=u.uid,
        quiz_type=QuizType.TERM2SENT,
        eligible=5,
        covered=0,
    )
    coverage = await fetch_coverage(rid, u.uid, expected.quiz_type)
    assert coverage == expected
    assert coverage.ratio == 0

    await generate_quiz(QuizType.TERM2SENT, CandidateType.ALL, aaa.uid, 3, u.uid)
    # 別タイプなので対象外
    await generate_quiz(QuizType.SENT2TERM, CandidateType.ALL, aaa.uid, 3, u.uid)

    # 別ユーザーなので対象外
    other = await aregister(email="quiz2@ex.com")
    await generate_quiz(QuizType.TERM2SENT, CandidateType.ALL, aaa.uid, 3, other.uid)

    expected = expected.model_copy(update={"covered": 1})
    coverage = await fetch_coverage(rid, u.uid, expected.quiz_type)
    assert coverage == expected
    assert coverage.ratio == pytest.approx(expected.covered / expected.eligible)


@mark_async_test()
async def test_fetch_uncovered(u: LUser):
    """リソース内の未クイズ化単文を作成."""
    ns = await fetch_namespace(u.uid)
    rid = ns.resources[0].uid
    aaa = LSentence.nodes.first(val="a")
    res = await fetch_uncovered_sent_ids(rid, u.uid, QuizType.TERM2SENT)
    assert aaa.uid in res  # クイズ作る前
    await generate_quiz(QuizType.TERM2SENT, CandidateType.ALL, aaa.uid, 3, u.uid)
    res = await fetch_uncovered_sent_ids(rid, u.uid, QuizType.TERM2SENT)
    assert aaa.uid not in res  # クイズ作成後は除外される


@mark_async_test()
async def test_fetch_covered(u: LUser):
    """リソース内のクイズ化単文を取得."""
    ns = await fetch_namespace(u.uid)
    rid = ns.resources[0].uid
    aaa = LSentence.nodes.first(val="a")
    res = await fetch_covered_sent_ids(rid, u.uid, QuizType.TERM2SENT)
    assert res == []  # クイズ作る前
    await generate_quiz(QuizType.TERM2SENT, CandidateType.ALL, aaa.uid, 3, u.uid)
    res = await fetch_covered_sent_ids(rid, u.uid, QuizType.TERM2SENT)
    assert res == [aaa.uid]  # クイズ作成後は含まれる


@mark_async_test()
async def test_sort_by_score(u: LUser):
    """スコア順で並べる."""
    ns = await fetch_namespace(u.uid)
    rid = ns.resources[0].uid
    res = await fetch_uncovered_sent_ids(rid, u.uid, QuizType.REL2PAIR)
    sort = await fetch_sort_by_score(res)
    kns = await fetch_knowdes_with_detail(sort, None)
    ls = list(kns.values())
    assert ls[0].sentence == "s"
    assert ls[1].sentence == "pre_s"


@mark_async_test()
async def test_fetch_target_ids(u: LUser):
    """poolからスコア順で指定件数の対象を取得."""
    ns = await fetch_namespace(u.uid)
    rid = ns.resources[0].uid
    s = LSentence.nodes.first(val="s")

    targets = await fetch_target_ids(
        rid,
        u.uid,
        QuizType.TERM2SENT,
        QuizTargetPool.UNCOVERED,
        QuizTargetOrder.HIGH_SCORE,
        limit=1,
    )
    assert targets == [s.uid]

    low_score_targets = await fetch_target_ids(
        rid,
        u.uid,
        QuizType.TERM2SENT,
        QuizTargetPool.UNCOVERED,
        QuizTargetOrder.LOW_SCORE,
        limit=1,
    )
    assert low_score_targets != targets

    await generate_quiz(QuizType.TERM2SENT, CandidateType.ALL, s.uid, 3, u.uid)

    targets = await fetch_target_ids(
        rid,
        u.uid,
        QuizType.TERM2SENT,
        QuizTargetPool.COVERED,
        QuizTargetOrder.HIGH_SCORE,
        limit=1,
    )
    assert targets == [s.uid]


@mark_async_test()
async def test_fetch_random_target_ids(u: LUser):
    """poolからランダムに指定件数の対象を取得."""
    ns = await fetch_namespace(u.uid)
    rid = ns.resources[0].uid
    pool = await fetch_uncovered_sent_ids(rid, u.uid, QuizType.TERM2SENT)
    limit = 2

    targets = await fetch_target_ids(
        rid,
        u.uid,
        QuizType.TERM2SENT,
        QuizTargetPool.UNCOVERED,
        QuizTargetOrder.RANDOM,
        limit=limit,
        rng=Random(0),  # noqa: S311
    )
    same_seed_targets = await fetch_target_ids(
        rid,
        u.uid,
        QuizType.TERM2SENT,
        QuizTargetPool.UNCOVERED,
        QuizTargetOrder.RANDOM,
        limit=limit,
        rng=Random(0),  # noqa: S311
    )

    assert len(targets) == limit
    assert set(targets) <= set(pool)
    assert targets == same_seed_targets


async def test_suggest_quizzes():
    """coverageとaccuracyから次に解くクイズを提案."""


async def test_accuracy():
    """正答率の取得.

    4種類のクイズごとに計算?
    sentence_accuracyという名前にしなかったのはそういうこと


    resource内の全単文のaccuracyをいちいち取得するのか?
    """


# fill_resource_coverage()
# fetch_resource_coverage()
# fetch_resource_accuracy()
