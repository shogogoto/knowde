"""test learning.

クイズ管理
  □ バッチ作成
  □ 正答率集計
  □ coverage算出
  □ クイズ提案.
"""

from knowde.conftest import async_fixture
from knowde.shared.user.label import LUser

from .fixture import fx_learning

u = async_fixture()(fx_learning)


async def test_fetch_resource_coverage(u: LUser):
    """リソースの正答率を取得."""
    # rs = await fetch_resources_by_user(u.uid)
    # ns = await fetch_namespace(u.uid)
    #
    # st = next(iter(ns.stats.values()))

    # await fetch_resource_stats_cache


# def test_jk
#
# get_quiz_coverage_by_resource()
# get_quiz_accuracy_by_resource()
# list_review_quiz_candidates()
# fill_resource_quizzes()
