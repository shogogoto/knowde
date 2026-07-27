"""test learning.

クイズ管理
  □ バッチ作成
  □ 正答率集計
  □ coverage算出
  □ クイズ提案.
"""

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.namespace import fetch_namespace
from knowde.feature.knowde.repo.detail import fetch_knowdes_with_detail
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.repo import (
    fetch_covered_sent_ids,
    fetch_sort_by_score,
    fetch_uncoverd_sent_ids,
)
from knowde.integration.quiz.repo.create import generate_quiz
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser

from .fixture import fx_learning

u = async_fixture()(fx_learning)


@mark_async_test()
async def test_fetch_coverage(u: LUser):
    """リソース内のクイズ化済み単文の割合を取得."""
    # rs = await fetch_resources_by_user(u.uid)
    # ns = await fetch_namespace(u.uid)
    # st = next(iter(ns.stats.values()))
    # await fetch_resource_stats_


@mark_async_test()
async def test_fetch_uncovered(u: LUser):
    """リソース内の未クイズ化単文を作成."""
    ns = await fetch_namespace(u.uid)
    rid = ns.resources[0].uid
    aaa = LSentence.nodes.first(val="a")
    res = await fetch_uncoverd_sent_ids(rid)
    assert aaa.uid in res  # クイズ作る前
    await generate_quiz(QuizType.TERM2SENT, CandidateType.ALL, aaa.uid, 3, u.uid)
    res = await fetch_uncoverd_sent_ids(rid)
    assert aaa.uid not in res  # クイズ作成後は除外される


@mark_async_test()
async def test_fetch_covered(u: LUser):
    """リソース内のクイズ化単文を取得."""
    ns = await fetch_namespace(u.uid)
    rid = ns.resources[0].uid
    aaa = LSentence.nodes.first(val="a")
    res = await fetch_covered_sent_ids(rid)
    assert list(res) == []  # クイズ作る前
    await generate_quiz(QuizType.TERM2SENT, CandidateType.ALL, aaa.uid, 3, u.uid)
    res = await fetch_covered_sent_ids(rid)
    assert list(res) == [aaa.uid]  # クイズ作成後は除外される


@mark_async_test()
async def test_sort_by_score(u: LUser):
    """スコア順で並べる."""
    ns = await fetch_namespace(u.uid)
    rid = ns.resources[0].uid
    res = await fetch_uncoverd_sent_ids(rid)
    sort = await fetch_sort_by_score(res)
    kns = await fetch_knowdes_with_detail(sort, None)
    ls = list(kns.values())
    assert ls[0].sentence == "s"
    assert ls[1].sentence == "pre_s"


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
