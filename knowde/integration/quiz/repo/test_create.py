"""誤答肢の生成."""

from neomodel import adb

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.domain.domain import QuizSource
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.learning.list import list_answers
from knowde.integration.quiz.repo.answer import create_answer
from knowde.integration.quiz.repo.fixture import fx_u
from knowde.shared.knowde.label import LSentence
from knowde.shared.types import UUIDy, to_uuid
from knowde.shared.user.label import LUser

from .create import check_duplicate_for_precreate, generate_quiz, prepare_quiz_gen

u = async_fixture()(fx_u)


# relクイズのたまにコケるのを発見しやすくするテスト
@mark_async_test()
async def test_prepare_quiz_gen(u: LUser):
    """タイプごとのクイズ生成."""

    async def _f(
        qt: QuizType,
        s_tgt: str,
        s_pair: str,
    ):
        tgt = LSentence.nodes.first(val=s_tgt)
        n_option = 3
        pair = LSentence.nodes.first(val=s_pair)
        _ds, _cor = await prepare_quiz_gen(
            qt,
            CandidateType.ALL,
            tgt.uid,
            n_option,
            [pair.uid],
        )

        # print(f"{sorted(ds)} {cor}")

    await _f(QuizType.REL2PAIR, "ccc", "parent")
    await _f(QuizType.PAIR2REL, "ccc", "parent")
    await _f(QuizType.REL2PAIR, "ccc", "parent")
    await _f(QuizType.PAIR2REL, "ccc", "parent")
    await _f(QuizType.REL2PAIR, "ccc", "parent")
    await _f(QuizType.PAIR2REL, "ccc", "parent")


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
    assert len(rq.options) == n_option
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
    n_option = 3  # テストデータが少ない
    src = await generate_quiz(
        qt,
        CandidateType.ALL,
        tgt.uid,
        n_option,
        user_id,
        correct_sent_uids=[pair.uid],  # ここの正解を自動で決定できるようにしたい
    )
    rq = src.to_readable()
    assert len(rq.options) == n_option
    k_cor = src.get_id_by_sent(s_pair)
    assert rq.is_correct([k_cor])
    incorrects = [s for s in src.readable_options() if s != k_cor]
    for inc in incorrects:
        assert not rq.is_correct([inc])


@mark_async_test()
async def test_gen_quiz(u: LUser):
    """タイプごとのクイズ生成."""
    await _check_with_term(QuizType.TERM2SENT, u.uid, "ccc", "ccc", "ccc1")
    await _check_with_term(QuizType.SENT2TERM, u.uid, "ccc", "ccc", "ccc1")
    await _check_gen_rel_quiz(QuizType.REL2PAIR, u.uid, "ccc", "parent")  # 偶に失敗
    await _check_gen_rel_quiz(QuizType.PAIR2REL, u.uid, "ccc", "parent")


@mark_async_test()
async def test_generated_quiz_has_creator_and_learner(u: LUser):
    """自分用に生成したクイズは作成者と学習者の両方に紐づく."""
    src = await _check_with_term(
        QuizType.TERM2SENT,
        u.uid,
        "ccc",
        "ccc",
        "ccc1",
    )
    rows, _ = await adb.cypher_query(
        """
        MATCH (user: User {uid: $user_id}), (quiz: Quiz {uid: $quiz_id})
        RETURN
            EXISTS { (user)-[:CREATE]->(quiz) },
            EXISTS { (user)-[:LEARN]->(quiz) }
        """,
        params={
            "user_id": to_uuid(u.uid).hex,
            "quiz_id": to_uuid(src.quiz_id).hex,
        },
    )
    assert rows == [[True, True]]


# 時々失敗する
@mark_async_test()
async def test_gen_quiz_no_correct_option(u: LUser):
    """クイズの正解の選択肢がなくて何も選ばないのが正解."""

    async def _check(qt: QuizType, n_option: int):
        tgt = LSentence.nodes.first(val="ccc")
        pair = LSentence.nodes.first(val="parent")
        src = await generate_quiz(
            qt,
            CandidateType.ALL,
            tgt.uid,
            n_option,
            u.uid,
            no_correct_option=True,
            correct_sent_uids=[pair.uid] if not qt.has_term else None,
        )
        rq = src.to_readable()
        assert len(rq.options) == n_option
        assert rq.is_correct([])

    await _check(QuizType.TERM2SENT, 3)
    await _check(QuizType.SENT2TERM, 3)
    await _check(QuizType.REL2PAIR, 3)
    await _check(QuizType.PAIR2REL, 3)


# クイズ作って質問を見て答える
@mark_async_test()
async def test_check_duplication(u: LUser):
    """クイズ作成の重複チェック."""

    async def _gen(
        qt: QuizType,
        user_id: UUIDy,
        s_tgt: str,
    ) -> QuizSource:
        tgt = LSentence.nodes.first(val=s_tgt)
        n_option = 5
        return await generate_quiz(qt, CandidateType.ALL, tgt.uid, n_option, user_id)

    src = await _gen(QuizType.TERM2SENT, u.uid, "ccc")
    assert await check_duplicate_for_precreate(
        src.target_id,
        src.quiz_type,
        list(src.sources.keys()),
        src.correct_ids,
    )
    assert not await check_duplicate_for_precreate(
        src.target_id,
        QuizType.REL2PAIR,  # 一部差し替えて不一致
        list(src.sources.keys()),
        src.correct_ids,
    )


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
