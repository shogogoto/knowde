"""列挙系."""

from pytest_unordered import unordered

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.candidate.types import CandidateType
from knowde.integration.quiz.distractor.distractor import fetch_distractor_ids
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.repo.create import create_quiz_and_correct
from knowde.integration.quiz.repo.fixture import fx_u
from knowde.shared.knowde.label import LSentence
from knowde.shared.types import UUIDy
from knowde.shared.user.label import LUser

from .list import (
    list_quiz_by_sentence_ids,
    list_quiz_by_user_ids,
)

u = async_fixture()(fx_u)


async def _create_quizzes_for_test(user_id: UUIDy, s_tgt: str) -> list[str]:
    """テストデータ作成."""
    qids = []
    types = [  # テキトーないくつか
        QuizType.TERM2SENT,
        QuizType.TERM2SENT,
        QuizType.SENT2TERM,
    ]
    sent = LSentence.nodes.first(val=s_tgt)
    for t in types:
        qid = await create_quiz_and_correct(
            sent.uid,
            t,
            await fetch_distractor_ids([sent.uid], CandidateType.NEAR, 3, True),  # noqa: FBT003
            user_uid=user_id,
        )
        qids.append(qid)
    return qids


@mark_async_test()
async def test_list_quiz_indipendent(u: LUser):
    """他のuserのクイズは取得されない."""
    u2 = await LUser(email="quiz2@ex.com").save()
    qids = await _create_quizzes_for_test(u.uid, "ccc")
    _ = await _create_quizzes_for_test(u2.uid, "ccc")
    qs = await list_quiz_by_user_ids([u.uid])
    assert [q.quiz_id for q in qs.data.root] == unordered(qids)


@mark_async_test()
async def test_list_quiz_by_sentence_id(u: LUser):
    """単文指定でクイズを取得."""
    sent = LSentence.nodes.first(val="ccc")
    qids = await _create_quizzes_for_test(u.uid, "ccc")
    _ = await _create_quizzes_for_test(u.uid, "ccc1")  # 別のクイズ
    qs = await list_quiz_by_sentence_ids([sent.uid])
    assert [q.quiz_id for q in qs.data.root] == unordered(qids)


@mark_async_test()
async def test_list_quiz_by_sentence_id_empty(u: LUser):
    """クイズが存在しない単文を指定した場合、空のリストが返る."""
    sent = LSentence.nodes.first(val="ccc")
    qs = await list_quiz_by_sentence_ids([sent.uid])
    assert len(qs.data.root) == 0


# resourceを指定してのクエリ
# 検索方式のenum指定
