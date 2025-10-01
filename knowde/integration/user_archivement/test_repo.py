"""test."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.resource.usecase import save_text
from knowde.shared.cypher import Paging
from knowde.shared.user.label import LUser

from .repo import fetch_user_with_current_achivement, snapshot_archivement


async def setup(username: str, count: int) -> LUser:  # noqa: D103
    u = await LUser(
        email=f"{username}@example.com",
        display_name=username,
        username=username,
    ).save()

    ss = [
        f"""
            # title{i}
              @author author{i}
              @published 10{i}/1/1
              a{i}
              b{i}
        """
        for i in reversed(range(1, count + 1))
    ]

    for s in ss:
        await save_text(u.uid, s)
    return u


@async_fixture()
async def us() -> list[LUser]:  # noqa: D103
    return [
        await setup("zero", 0),
        await setup("one", 1),
        await setup("two", 2),
        await setup("three", 3),
    ]


@mark_async_test()
async def test_fetch_user_by_score(us: list[LUser]):
    """Aaaa."""
    res = await fetch_user_with_current_achivement()
    # paging
    res1 = await fetch_user_with_current_achivement(paging=Paging(page=1, size=3))
    assert len(res1.data) == 3  # noqa: PLR2004
    res2 = await fetch_user_with_current_achivement(paging=Paging(page=2, size=3))
    assert len(res2.data) == 1
    res3 = await fetch_user_with_current_achivement(paging=Paging(page=3, size=3))
    assert len(res3.data) == 0
    assert res.total == res1.total == res2.total == res3.total == 4  # noqa: PLR2004

    # ユーザー名検索
    res = await fetch_user_with_current_achivement("zero")
    assert len(res.data) == res.total == 1
    res = await fetch_user_with_current_achivement("four")
    assert len(res.data) == res.total == 0

    # ソート
    res = await fetch_user_with_current_achivement("", keys=["username"], desc=True)
    assert [r.user.username for r in res.data] == ["zero", "two", "three", "one"]
    res = await fetch_user_with_current_achivement("", keys=["username"], desc=False)
    assert [r.user.username for r in res.data] == ["one", "three", "two", "zero"]

    # ソート by archivement
    res = await fetch_user_with_current_achivement("", keys=["n_sentence"])
    assert [r.user.username for r in res.data] == ["three", "two", "one", "zero"]
    assert [r.archivement.n_resource for r in res.data] == [3, 2, 1, 0]


@mark_async_test()
async def test_snapshot_archivement(us: list[LUser]):
    """成果スナップショット."""
    # await setup("zero", 0)
    # await setup("one", 1)
    # await setup("two", 2)
    # await setup("three", 3)
    # print("#" * 80)
    _res = await snapshot_archivement()
    # print(res)
    # res = await snapshot_archivement()
    # print(res)
    # res = await snapshot_archivement()
    # print(res)
    # res = await fetch_user_with_achivement()
    # assert len(res.data) == 4()

    # sleep(10000)
    # raise AssertionError
