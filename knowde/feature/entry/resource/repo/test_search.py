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
        for i in range(1, 5)
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
    rs = await search_resources("")
    assert rs.total == 5  # noqa: PLR2004

    # ユーザー検索
    urs = await search_resources("", search_user="two")
    assert urs.total == len(urs.data) == 1
    assert urs.data[0].user.username == "two"
    assert urs.data[0].resource.name == "# other user"
    # print([r.resource.published for r in rs.data])
