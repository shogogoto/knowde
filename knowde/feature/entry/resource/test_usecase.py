"""test resource usecase.

cache 有無 / resource 有無 でテスト
"""

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.namespace import create_resource, fetch_namespace
from knowde.feature.entry.resource.usecase import (
    save_resource_with_detail,
)
from knowde.shared.user.label import LUser


@async_fixture()
async def u() -> LUser:  # noqa: D103
    return await LUser(email="one@gmail.com").save()


@mark_async_test()
async def test_save_resource_with_detail_unsaved_uncached(u: LUser):
    """Resource unsaved & cacheなし => resourceもcacheが作成される."""
    s = """
        # title1
          aaa
    """
    ns = await fetch_namespace(u.uid)
    assert len(ns.g.nodes) == 0
    assert len(ns.stats.values()) == 0

    await save_resource_with_detail(ns, s)
    ns = await fetch_namespace(u.uid)
    assert len(ns.stats.values()) == 1


@mark_async_test()
async def test_save_resource_with_detail_saved_uncached(u: LUser):
    """Resource 既にsaved & cacheなし => cacheが作成される."""
    s = """
        # title1
          aaa
    """
    await create_resource(u.uid, "# title1")
    ns = await fetch_namespace(u.uid)

    assert len(ns.g.nodes) == 1
    assert len(ns.stats.values()) == 0

    await save_resource_with_detail(ns, s)
    ns = await fetch_namespace(u.uid)
    assert len(ns.g.nodes) == 1
    assert len(ns.stats.values()) == 1


@mark_async_test()
async def test_save_resource_with_detail_saved_cached(u: LUser):
    """Resource 既にsaved & cacheある => cacheが更新される."""
    s = """
        # title1
          aaa
    """
    ns = await fetch_namespace(u.uid)
    await save_resource_with_detail(ns, s)
    ns = await fetch_namespace(u.uid)
    rid = ns.get_resource("# title1").uid.hex
    assert len(ns.g.nodes) == 1
    assert ns.stats[rid].n_sentence == 1

    s2 = """
        # title1
          aaa
          bbb
    """
    await save_resource_with_detail(ns, s2)
    ns = await fetch_namespace(u.uid)
    assert len(ns.g.nodes) == 1
    assert ns.stats[rid].n_sentence == 2  # noqa: PLR2004
