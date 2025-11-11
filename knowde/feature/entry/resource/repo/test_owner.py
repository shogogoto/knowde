"""リソース所有者判定test."""

from uuid import uuid4

import pytest

from knowde.conftest import mark_async_test
from knowde.feature.entry.label import LResource
from knowde.feature.entry.resource.repo.owner import check_entry_owner
from knowde.feature.entry.resource.usecase import save_text
from knowde.shared.errors.domain import NotFoundError
from knowde.shared.user.label import LUser


@mark_async_test()
async def test_check_entry_owner():
    """リソースの所有者か判定."""
    u1 = await LUser(email="one@gmail.com").save()
    u2 = await LUser(email="two@gmail.com").save()
    _, mr = await save_text(u1.uid, "# title1\n")

    with pytest.raises(NotFoundError):  # entry not found
        await check_entry_owner(u1.uid, uuid4())
    with pytest.raises(NotFoundError):  # user not found
        await check_entry_owner(uuid4(), mr.uid)

    r_without_owner = await LResource(title="# xxx").save()
    assert not await check_entry_owner(u1.uid, r_without_owner.uid)

    # 別ユーザー
    assert await check_entry_owner(u1.uid, mr.uid)
    assert not await check_entry_owner(u1.uid, r_without_owner.uid)

    # 階層が深い
    _, mr = await save_text(u1.uid, "# title2\n", ("sub1", "sub2"))
    assert await check_entry_owner(u1.uid, mr.uid)
    assert not await check_entry_owner(u2.uid, mr.uid)
