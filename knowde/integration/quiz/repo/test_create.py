"""誤答肢の生成."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.candidate.candidate import (
    list_candidates_by_radius,
)
from knowde.integration.quiz.domain.build import build_readable
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.integration.quiz.sampling.sample_safe import (
    sample_safe,
)
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser

from .create import (
    create_quiz,
)

u = async_fixture()(fx_u)


# クイズ作って質問を見て答える
@mark_async_test()
async def test_create_restore_term2sent(u: LUser):
    """単文当てクイズを永続化&復元."""
    sent = LSentence.nodes.first(val="ccc")
    n_option = 5
    cand_uids = await list_candidates_by_radius(sent.uid, radius=99, has_term=True)
    sample_uids = sample_safe(cand_uids, n_option=n_option)
    quiz_uid = await create_quiz(sent.uid, QuizType.TERM2SENT, sample_uids)
    srcs = await restore_quiz_sources([quiz_uid])
    assert len(srcs) == 1
    src = srcs[0]
    assert len(src.sources) == n_option - 1
    rq = build_readable(src)
    # print(rq.string)
    assert rq.is_correct([src.get_id_by_sent("ccc")])
    assert not rq.is_correct([src.get_id_by_sent("ccc1")])


@mark_async_test()
async def test_create_restore_sent2term(u: LUser):
    """用語当てクイズを永続化&復元."""
    sent = LSentence.nodes.first(val="ccc")
    n_option = 5
    cand_uids = await list_candidates_by_radius(sent.uid, radius=99, has_term=True)
    sample_uids = sample_safe(cand_uids, n_option=n_option)
    quiz_uid = await create_quiz(sent.uid, QuizType.SENT2TERM, sample_uids)
    srcs = await restore_quiz_sources([quiz_uid])
    src = srcs[0]
    # print(src.model_dump_json(indent=2))
    rq = build_readable(src)
    # print(rq.string)
    assert rq.is_correct([src.get_id_by_sent("ccc")])
    assert not rq.is_correct([src.get_id_by_sent("ccc1")])


@mark_async_test()
async def test_create_restore_rel2pair(u: LUser):
    """関係からペアを当てる."""
    # ccc の 親の単文を当てろ
    tgt = LSentence.nodes.first(val="ccc")
    pair = LSentence.nodes.first(val="parent")
    n_option = 4

    cand_uids = await list_candidates_by_radius(tgt.uid, radius=3)
    sample_uids = sample_safe(cand_uids, n_option=n_option)
    quiz_uid = await create_quiz(
        tgt.uid,
        QuizType.REL2PAIR,
        sample_uids,
        [pair.uid],
    )
    srcs = await restore_quiz_sources([quiz_uid])
    src = srcs[0]
    # print(src.model_dump_json(indent=2))
    rq = build_readable(src)
    # print(rq.string)
    assert rq.is_correct([src.get_id_by_sent("parent")])
    incorrects = [s.sentence for s in src.sources.values() if s.sentence != "parent"]
    for inc in incorrects:
        assert not rq.is_correct([src.get_id_by_sent(inc)])


@mark_async_test()
async def test_create_restore_pair2rel(u: LUser):
    """ペアの関係当てクイズ."""
    tgt = LSentence.nodes.first(val="ccc")
    pair = LSentence.nodes.first(val="parent")
    n_option = 4

    cand_uids = await list_candidates_by_radius(tgt.uid, radius=3)
    sample_uids = sample_safe(cand_uids, n_option=n_option)
    quiz_uid = await create_quiz(
        tgt.uid,
        QuizType.PAIR2REL,
        sample_uids,
        [pair.uid],
    )
    srcs = await restore_quiz_sources([quiz_uid])
    src = srcs[0]
    # print(src.model_dump_json(indent=2))
    rq = build_readable(src)
    # print(rq.string)
    assert rq.is_correct([src.get_id_by_sent("parent")])
    incorrects = [s.sentence for s in src.sources.values() if s.sentence != "parent"]
    for inc in incorrects:
        assert not rq.is_correct([src.get_id_by_sent(inc)])
