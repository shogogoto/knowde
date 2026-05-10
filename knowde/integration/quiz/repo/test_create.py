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

from .create import create_answer, create_quiz_and_correct, generate_quiz

u = async_fixture()(fx_u)


@mark_async_test()
async def test_gen_term2sent_quiz(u: LUser):
    """単文当てクイズを永続化&復元."""
    n_option = 5
    tgt = LSentence.nodes.first(val="ccc")
    rq, src = await generate_quiz(
        QuizType.TERM2SENT,
        CandidateType.ALL,
        tgt.uid,
        n_option,
        u.uid,
    )
    # print(rq.string)
    assert len(rq.options.values()) == n_option
    assert rq.is_correct([src.get_id_by_sent("ccc")])
    assert not rq.is_correct([src.get_id_by_sent("ccc1")])


@mark_async_test()
async def test_gen_sent2term_quiz(u: LUser):
    """用語当てクイズを永続化&復元."""
    n_option = 5
    tgt = LSentence.nodes.first(val="ccc")
    rq, src = await generate_quiz(
        QuizType.SENT2TERM,
        CandidateType.ALL,
        tgt.uid,
        n_option,
        u.uid,
    )
    # print(rq.string)
    assert len(rq.options.values()) == n_option
    assert rq.is_correct([src.get_id_by_sent("ccc")])
    assert not rq.is_correct([src.get_id_by_sent("ccc1")])


@mark_async_test()
async def test_create_restore_rel2pair(u: LUser):
    """関係からペアを当てる."""
    # ccc の 親の単文を当てろ
    tgt = LSentence.nodes.first(val="ccc")
    pair = LSentence.nodes.first(val="parent")
    n_option = 5
    # print(src.model_dump_json(indent=2))
    rq, src = await generate_quiz(
        QuizType.REL2PAIR,
        CandidateType.ALL,
        tgt.uid,
        n_option,
        u.uid,
        correct_sent_uids=[pair.uid],
    )
    # print(rq.string)
    assert len(rq.options.values()) == n_option
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
    rq, src = await generate_quiz(
        QuizType.PAIR2REL,
        CandidateType.ALL,
        tgt.uid,
        n_option,
        u.uid,
        correct_sent_uids=[pair.uid],
    )
    # print(rq.string)
    assert len(rq.options.values()) == n_option
    assert rq.is_correct([src.get_id_by_sent("parent")])
    incorrects = [s.sentence for s in src.sources.values() if s.sentence != "parent"]
    for inc in incorrects:
        assert not rq.is_correct([src.get_id_by_sent(inc)])


@mark_async_test()
async def test_duplicate_option_exception(u: LUser):
    """選択肢が重複することがあるので直せ."""


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
