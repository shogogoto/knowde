"""test repo."""

from knowde.conftest import mark_async_test
from knowde.feature.entry.namespace import create_resource
from knowde.feature.parsing.tree2net import parse2net
from knowde.shared.user.label import LUser

from .repo import save_resource_stats_cache


@mark_async_test()
async def test_new_and_update_stat_cache():
    """リソース統計情報の新規作成と更新."""
    u = await LUser(email="one@gmail.com").save()
    lr = await create_resource(u.uid, "# r1")

    s = """
        # r1
        ## title1
          aaa
          bbb
    """
    sn = parse2net(s)

    lb1 = await save_resource_stats_cache(lr.uid, sn)
    lb2 = await save_resource_stats_cache(lr.uid, sn)
    assert lb1.element_id == lb2.element_id
