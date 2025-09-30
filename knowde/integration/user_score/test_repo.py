"""test."""

from knowde.feature.entry.resource.usecase import save_text
from knowde.integration.user_score.repo import fetch_user_with_achivement
from knowde.shared.cypher import Paging
from knowde.shared.user.label import LUser


async def setup(username: str, count: int) -> LUser:  # noqa: D103
    u = await LUser(
        email=f"{username}@gmail.com",
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


async def test_fetch_user_by_score():
    """Aaaa."""
    await setup("zero", 0)
    await setup("one", 1)
    await setup("two", 2)
    await setup("three", 3)

    res = await fetch_user_with_achivement()
    # paging
    res1 = await fetch_user_with_achivement(paging=Paging(page=1, size=3))
    assert len(res1.data) == 3  # noqa: PLR2004
    res2 = await fetch_user_with_achivement(paging=Paging(page=2, size=3))
    assert len(res2.data) == 1
    res3 = await fetch_user_with_achivement(paging=Paging(page=3, size=3))
    assert len(res3.data) == 0
    assert res.total == res1.total == res2.total == res3.total == 4  # noqa: PLR2004

    # ユーザー名検索
    res = await fetch_user_with_achivement("zero")
    assert len(res.data) == 1
    res = await fetch_user_with_achivement("four")
    assert len(res.data) == 0

    # sort

    # assert len(rows) == 10
    # print(res.model_dump_json(indent=2))
