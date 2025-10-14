"""リソース所有者判定test."""

from uuid import uuid4

import pytest

from knowde.conftest import mark_async_test
from knowde.feature.entry.label import LResource
from knowde.feature.entry.resource.repo.owner import is_resource_owner
from knowde.feature.entry.resource.usecase import save_text
from knowde.shared.errors.domain import NotFoundError
from knowde.shared.user.label import LUser


@mark_async_test()
async def test_is_owner():
    """リソースの所有者か判定."""
    u1 = await LUser(email="one@gmail.com").save()
    u2 = await LUser(email="two@gmail.com").save()
    _, mr = await save_text(u1.uid, "# title1\n")

    with pytest.raises(NotFoundError):
        await is_resource_owner(u1.uid, uuid4())

    r = await LResource(title="# xxx").save()
    with pytest.raises(NotFoundError):
        await is_resource_owner(u1.uid, r.uid)

    assert await is_resource_owner(u1.uid, mr.uid)
    assert not await is_resource_owner(u2.uid, mr.uid)
