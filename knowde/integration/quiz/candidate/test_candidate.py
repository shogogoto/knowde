"""誤答肢."""

import pytest
from pydantic import ValidationError

from knowde.conftest import mark_async_test
from knowde.feature.entry.resource.usecase import save_text
from knowde.integration.quiz.fixture import fx_u
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser

from .candidate import (
    _list_candidates_in_resource,
    list_candidates_by_radius,
    list_top_scoring_candidates,
)


async def u() -> LUser:  # noqa: D103
    s = """
    # title2
        A: aaa
            xxxx
        B: bbb
        C: ccc
    """
    u = await LUser(email="select_option@ex.com").save()
    await save_text(u.uid, s)
    return u


@mark_async_test()
async def test_list_candidates_in_resource():
    """リソース内検索."""
    await u()
    sent = LSentence.nodes.first(val="aaa")
    c = await _list_candidates_in_resource(sent.uid)
    assert len(c) == 3  # noqa: PLR2004
    c = await _list_candidates_in_resource(sent.uid, must_has_term=True)
    assert len(c) == 2  # noqa: PLR2004


@mark_async_test()
async def test_list_candidates_by_radius():
    """距離指定で誤答肢候補を列挙."""
    await u()
    sent = LSentence.nodes.first(val="aaa")
    with pytest.raises(ValidationError):
        await list_candidates_by_radius(sent.uid, radius=-999)
    c = await list_candidates_by_radius(sent.uid, radius=1)
    assert len(c) == 2  # noqa: PLR2004
    c = await list_candidates_by_radius(sent.uid, radius=2)
    assert len(c) == 3  # noqa: PLR2004

    # 用語あり
    c = await list_candidates_by_radius(sent.uid, radius=1, must_has_term=True)
    assert len(c) == 1
    c = await list_candidates_by_radius(sent.uid, radius=2, must_has_term=True)
    assert len(c) == 2  # noqa: PLR2004


@mark_async_test()
async def test_list_top_scoring_candidates():
    """対象と特定の関係をもつ候補を列挙する."""
    await fx_u()
    sent = LSentence.nodes.first(val="aaa")
    # 用語ありなのは5個
    res = await list_top_scoring_candidates(sent.uid, 999, must_has_term=True)
    assert len(res) == 5  # noqa: PLR2004

    # 単文全てで16個 (対象を除く)
    res = await list_top_scoring_candidates(sent.uid, 999, must_has_term=False)
    assert len(res) == 15  # noqa: PLR2004
