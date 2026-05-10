"""誤答肢の生成."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.distractor.distractor import fetch_distractor_ids
from knowde.integration.quiz.domain.build import build_readable
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.repo.list_query import list_answers
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser

from .create import create_answer, create_quiz_and_correct

u = async_fixture()(fx_u)


async def _sample(n_option: int):
    sent = LSentence.nodes.first(val="ccc")
    ds = await fetch_distractor_ids(
        [sent.uid],
        CandidateType.ALL,
        n_option - 1,
        True,  # noqa: FBT003
    )
    return sent.uid, ds


# クイズ作って質問を見て答える
@mark_async_test()
async def test_create_restore_term2sent(u: LUser):
    """単文当てクイズを永続化&復元."""
    n_option = 5
    sent_uid, sample_uids = await _sample(n_option)
    quiz_uid = await create_quiz_and_correct(sent_uid, QuizType.TERM2SENT, sample_uids)
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
    n_option = 5
    sent_uid, sample_uids = await _sample(n_option)
    quiz_uid = await create_quiz_and_correct(sent_uid, QuizType.SENT2TERM, sample_uids)
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
    ds = await fetch_distractor_ids([tgt.uid], CandidateType.MID, n_option - 1, True)  # noqa: FBT003
    quiz_uid = await create_quiz_and_correct(
        tgt.uid,
        QuizType.REL2PAIR,
        ds,
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
    ds = await fetch_distractor_ids([tgt.uid], CandidateType.MID, n_option - 1, True)  # noqa: FBT003
    quiz_uid = await create_quiz_and_correct(
        tgt.uid,
        QuizType.PAIR2REL,
        ds,
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


# クイズ作って質問を見て答える
@mark_async_test()
async def test_answer(u: LUser):
    """回答してリストや正答率を返す."""
    sent = LSentence.nodes.first(val="ccc")
    n_option = 5
    ds = await fetch_distractor_ids([sent.uid], CandidateType.ALL, n_option - 1, True)  # noqa: FBT003
    quiz_uid = await create_quiz_and_correct(
        sent.uid,
        QuizType.TERM2SENT,
        ds,
        user_uid=u.uid,
    )
    anss = await list_answers([quiz_uid], user_uid=u.uid)
    assert len(anss.root) == 0
    srcs = await restore_quiz_sources([quiz_uid])
    rq = build_readable(srcs[0])
    # print()
    # print(rq.string)
    ans1 = await create_answer(
        rq.quiz_id,
        selected_uids=rq.correct,
        user_uid=u.uid,
    )
    assert ans1.is_correct
    anss = await list_answers([quiz_uid], user_uid=u.uid)
    assert len(anss.root) == 1

    incorrect = LSentence.nodes.first(val="todetail")
    ans2 = await create_answer(
        rq.quiz_id,
        selected_uids=[incorrect.uid],
        user_uid=u.uid,
    )
    assert not ans2.is_correct
    anss = await list_answers([quiz_uid], user_uid=u.uid)
    assert len(anss.root) == 2  # noqa: PLR2004


@mark_async_test()
async def test_batch_create_quiz_by_user():
    """クイズ一括作成 resource横断."""


@mark_async_test()
async def test_batch_create_quiz_one_resource():
    """クイズ一括作成 特定resource."""
