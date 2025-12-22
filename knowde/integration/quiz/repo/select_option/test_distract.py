"""誤答肢."""

import pytest
from pydantic import ValidationError

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.resource.usecase import save_text
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser

from .distract import (
    list_candidates_by_radius,
    list_candidates_in_resource,
)


@async_fixture()
async def u() -> LUser:  # noqa: D103
    return await LUser(email="quiz@ex.com").save()


@mark_async_test()
async def test_list_candidates_in_resource(u: LUser):
    """リソース内検索."""
    s = """
    # title
        A: aaa
            xxxx
        B: bbb
        C: ccc
    """
    await save_text(u.uid, s)
    sent = LSentence.nodes.first(val="aaa")
    c = await list_candidates_in_resource(sent.uid)
    assert len(c) == 3  # noqa: PLR2004
    c = await list_candidates_in_resource(sent.uid, has_term=True)
    assert len(c) == 2  # noqa: PLR2004


@mark_async_test()
async def test_list_candidates_by_radius(u: LUser):
    """距離指定で誤答肢候補を列挙."""
    s = """
    # title
        A: aaa
            xxxx
        B: bbb
        C: ccc
    """
    await save_text(u.uid, s)
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


# @mark_async_test()
# async def test_list_distractor_with_rel(u: LUser):
#     """関係を指定して誤答肢候補を列挙."""
#     s = """
#     # title
#         A: aaa
#             xxxx
#         B: bbb
#         C: ccc
#     """
#
#     await save_text(u.uid, s)
#
#     sent = LSentence.nodes.first(val="aaa")
#     c = await list_candidates_by_dist(sent.uid, has_term=True)
#     assert len(c) == 1
