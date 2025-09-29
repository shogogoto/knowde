"""test search resource."""

from knowde.conftest import mark_async_test
from knowde.feature.entry.resource.repo.search import (
    search_resources,
)
from knowde.feature.entry.resource.usecase import save_text
from knowde.feature.knowde.repo.clause import Paging
from knowde.shared.user.label import LUser


async def setup() -> LUser:  # noqa: D103
    u = await LUser(
        email="one@gmail.com",
        display_name="one",
    ).save()

    ss = [
        f"""
            # title{i}
              @author author{i}
              @published 10{i}/1/1
            ## head1
              a{i}
              b{i}
        """
        for i in reversed(range(1, 5))
    ]

    for s in ss:
        await save_text(u.uid, s)
    return u


@mark_async_test()
async def test_search_resources() -> None:
    """リソース総数を取得."""
    await setup()
    # paging
    rs1 = await search_resources("")
    assert len(rs1.data) == rs1.total == 4  # noqa: PLR2004
    rs2 = await search_resources("", Paging(page=1, size=3))
    assert len(rs2.data) == 3  # noqa: PLR2004
    rs3 = await search_resources("", Paging(page=2, size=3))
    assert len(rs3.data) == 1
    rs4 = await search_resources("", Paging(page=3, size=3))
    assert len(rs4.data) == 0
    assert rs1.total == rs2.total == rs3.total == rs4.total

    u2 = await LUser(email="two@gmail.com", username="two").save()
    await save_text(
        u2.uid,
        """
        # other user
        ## title1
    """,
    )
    rs_asc = await search_resources("", keys=["title"], desc=False)
    assert [r.resource.name for r in rs_asc.data] == [
        "# other user",
        "# title1",
        "# title2",
        "# title3",
        "# title4",
    ]
    rs_desc = await search_resources("", keys=["title"], desc=True)
    assert rs_desc.total == rs_asc.total == 5  # noqa: PLR2004
    assert [r.resource.name for r in rs_desc.data] == [
        "# title4",
        "# title3",
        "# title2",
        "# title1",
        "# other user",
    ]

    # ユーザー検索
    urs = await search_resources("", search_user="two")
    assert urs.total == len(urs.data) == 1
    assert urs.data[0].user.username == "two"
    assert urs.data[0].resource.name == "# other user"

    # authorで検索 パフォーマンス悪化を懸念してやめとく
    # ars = await search_resources("author1")
    # assert len(ars.data) == ars.total == 1
    # assert list(ars.data[0].resource.authors) == unordered(["author1"])


@mark_async_test()
async def test_search_resources_range() -> None:
    """範囲検索."""
    # u = await LUser(email="one@gmail.com").save()
    # s1 = """
    #     # title1
    #
    # """
    # stats で sort

    # updatedを絞る
    # publishedを絞る
