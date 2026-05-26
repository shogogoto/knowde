"""誤答肢の生成."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.domain import QuizSource
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.repo.fixture import fx_u
from knowde.integration.quiz.repo.list_query import list_answers
from knowde.shared.knowde.label import LSentence
from knowde.shared.types import UUIDy
from knowde.shared.user.label import LUser

from .answer import create_answer
from .create import generate_quiz

u = async_fixture()(fx_u)


async def _check_with_term(
    qt: QuizType,
    user_id: UUIDy,
    s_tgt: str,
    s_corrent: str,
    s_uncorrect: str,
) -> QuizSource:
    tgt = LSentence.nodes.first(val=s_tgt)
    n_option = 5
    src = await generate_quiz(qt, CandidateType.ALL, tgt.uid, n_option, user_id)
    rq = src.to_readable()
    assert rq.is_correct([src.get_id_by_sent(s_corrent)])
    assert not rq.is_correct([src.get_id_by_sent(s_uncorrect)])
    return src


async def _check_gen_rel_quiz(
    qt: QuizType,
    user_id: UUIDy,
    s_tgt: str,
    s_pair: str,
):
    tgt = LSentence.nodes.first(val=s_tgt)
    pair = LSentence.nodes.first(val=s_pair)
    n_option = 3
    src = await generate_quiz(
        qt,
        CandidateType.ALL,
        tgt.uid,
        n_option,
        user_id,
        correct_sent_uids=[pair.uid],  # ここの正解を自動で決定できるようにしたい
    )
    rq = src.to_readable()
    assert rq.is_correct([src.get_id_by_sent(s_pair)])
    incorrects = [s.sentence for s in src.sources.values() if s.sentence != s_pair]
    for inc in incorrects:
        assert not rq.is_correct([src.get_id_by_sent(inc)])


# 正解と選択肢を作成するロジックを分離できそう
@mark_async_test()
async def test_gen_quiz(u: LUser):
    """タイプごとのクイズ生成."""
    await _check_with_term(QuizType.TERM2SENT, u.uid, "ccc", "ccc", "ccc1")
    await _check_with_term(QuizType.SENT2TERM, u.uid, "ccc", "ccc", "ccc1")
    await _check_gen_rel_quiz(QuizType.REL2PAIR, u.uid, "ccc", "parent")
    # たまに失敗する?
    await _check_gen_rel_quiz(QuizType.PAIR2REL, u.uid, "ccc", "parent")


@mark_async_test()
async def test_gen_quiz_no_correct_option(u: LUser):
    """クイズの正解の選択肢がなくて何も選ばないのが正解."""


# クイズ作って質問を見て答える
@mark_async_test()
async def test_answer(u: LUser):
    """回答してリストや正答率を返す."""
    src = await _check_with_term(QuizType.TERM2SENT, u.uid, "ccc", "ccc", "ccc1")
    rq = src.to_readable()

    async def _check_answer_count(n: int):
        anss = await list_answers([rq.quiz_id], user_uid=u.uid)
        assert len(anss.root) == n

    await _check_answer_count(0)
    ans1 = await create_answer(rq.quiz_id, rq.correct, u.uid)
    assert ans1.is_correct
    await _check_answer_count(1)

    incorrect = LSentence.nodes.first(val="todetail")
    ans2 = await create_answer(rq.quiz_id, [incorrect.uid], u.uid)
    assert not ans2.is_correct
    await _check_answer_count(2)
