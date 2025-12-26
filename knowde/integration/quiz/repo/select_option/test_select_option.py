"""誤答肢."""

import pytest
from pydantic import ValidationError

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.resource.usecase import save_text
from knowde.integration.quiz.errors import SamplingError
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.repo.select_option.selector import select_random_options
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser

from .candidate import (
    _list_candidates_in_resource,
    list_candidates_by_radius,
)


@async_fixture()
async def u() -> LUser:  # noqa: D103
    s = """
    # title
        A: aaa
            xxxx
        B: bbb
        C: ccc
    """
    u = await LUser(email="select_option@ex.com").save()
    await save_text(u.uid, s)
    return u


@mark_async_test()
async def test_list_candidates_in_resource(u: LUser):
    """リソース内検索."""
    sent = LSentence.nodes.first(val="aaa")
    c = await _list_candidates_in_resource(sent.uid)
    assert len(c) == 3  # noqa: PLR2004
    c = await _list_candidates_in_resource(sent.uid, has_term=True)
    assert len(c) == 2  # noqa: PLR2004


@mark_async_test()
async def test_list_candidates_by_radius(u: LUser):
    """距離指定で誤答肢候補を列挙."""
    sent = LSentence.nodes.first(val="aaa")
    with pytest.raises(ValidationError):
        await list_candidates_by_radius(sent.uid, radius=-999)
    c = await list_candidates_by_radius(sent.uid, radius=1)
    assert len(c) == 2  # noqa: PLR2004
    c = await list_candidates_by_radius(sent.uid, radius=2)
    assert len(c) == 3  # noqa: PLR2004

    # 用語あり
    c = await list_candidates_by_radius(sent.uid, radius=1, has_term=True)
    assert len(c) == 1
    c = await list_candidates_by_radius(sent.uid, radius=2, has_term=True)
    assert len(c) == 2  # noqa: PLR2004


uu = async_fixture()(fx_u)


@mark_async_test()
async def test_select_sample_retry(uu: LUser):
    """選択肢の数を満たすようにretryを繰り返す."""
    sent = LSentence.nodes.first(val="ccc")

    with pytest.raises(SamplingError):
        await select_random_options(sent.uid, radius=1, n_option=100, n_retry=100)

    #  使用しているfixtureでは用語は4つまでしかない
    await select_random_options(sent.uid, radius=1, n_option=4, n_retry=5)
