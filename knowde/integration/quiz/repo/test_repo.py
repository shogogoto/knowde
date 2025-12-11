"""誤答肢の生成."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.resource.usecase import save_text
from knowde.integration.quiz.repo.distract import list_distractor_candidates
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser


@async_fixture()
async def u() -> LUser:  # noqa: D103
    return await LUser(email="quiz@ex.com").save()


@mark_async_test()
async def test_list_distractor_candidates(u: LUser):
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
    c = await list_distractor_candidates(sent.uid)
    assert len(c) == 3  # noqa: PLR2004
    c = await list_distractor_candidates(sent.uid, dist=1)
    assert len(c) == 2  # noqa: PLR2004
    c = await list_distractor_candidates(sent.uid, dist=2)
    assert len(c) == 3  # noqa: PLR2004

    c = await list_distractor_candidates(sent.uid, dist=1, has_term=True)
    assert len(c) == 1
    c = await list_distractor_candidates(sent.uid, dist=2, has_term=True)
    assert len(c) == 2  # noqa: PLR2004


@mark_async_test()
async def test_choose_distractor_by_score(u: LUser):
    """誤答候補から誤答を選択する."""
