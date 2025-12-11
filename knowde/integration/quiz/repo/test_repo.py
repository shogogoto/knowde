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
async def test_distractor_sent2term(u: LUser):
    """単文に対して用語選択肢を当てる."""
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
