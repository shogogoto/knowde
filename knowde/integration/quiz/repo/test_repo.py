"""誤答肢の生成."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.domain.build import build_readable
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.repo.repo import (
    create_quiz,
)
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.integration.quiz.repo.select_option.candidate import (
    list_candidates_by_radius,
)
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser

from .select_option.sample import sample_options_randomly

u = async_fixture()(fx_u)


# クイズ作って質問を見て答える
@mark_async_test()
async def test_create_restore_term2sent(u: LUser):
    """単文当てクイズを永続化&復元."""
    sent = LSentence.nodes.first(val="ccc")
    n_option = 5
    cand_uids = await list_candidates_by_radius(sent.uid, radius=99, has_term=True)
    sample_uids = sample_options_randomly(cand_uids, n_option=n_option)
    quiz_uid = await create_quiz(sent.uid, QuizType.TERM2SENT, sample_uids)
    srcs = await restore_quiz_sources([quiz_uid])
    assert len(srcs) == 1
    src = srcs[0]
    assert len(src.sources) == n_option - 1
    rq = build_readable(src)
    # print(rq.string)
    assert rq.answer([src.get_id_by_sent("ccc")]).is_corrent()
    assert not rq.answer([src.get_id_by_sent("ccc1")]).is_corrent()


@mark_async_test()
async def test_create_restore_sent2term(u: LUser):
    """用語当てクイズを永続化&復元."""
    sent = LSentence.nodes.first(val="ccc")
    n_option = 5
    cand_uids = await list_candidates_by_radius(sent.uid, radius=99, has_term=True)
    sample_uids = sample_options_randomly(cand_uids, n_option=n_option)
    quiz_uid = await create_quiz(sent.uid, QuizType.SENT2TERM, sample_uids)
    srcs = await restore_quiz_sources([quiz_uid])
    src = srcs[0]
    # print(src.model_dump_json(indent=2))
    rq = build_readable(src)
    # print(rq.string)
    assert rq.answer([src.get_id_by_sent("ccc")]).is_corrent()
    assert not rq.answer([src.get_id_by_sent("ccc1")]).is_corrent()
