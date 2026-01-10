"""列挙系."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.repo.create import create_quiz
from knowde.integration.quiz.repo.quiz_repo import (
    list_quiz_by_sentence_ids,
    list_quiz_by_user_ids,
)
from knowde.integration.quiz.repo.select_option.selector import (
    retry_select_random_options,
)
from knowde.shared.knowde.label import LSentence
from knowde.shared.types import UUIDy
from knowde.shared.user.label import LUser

u = async_fixture()(fx_u)


async def _f(sent_id: UUIDy):
    return await retry_select_random_options(
        sent_id,
        radius=3,
        n_option=4,
        has_term=True,
    )


async def setup(sent_id: UUIDy, user_id: UUIDy) -> list[str]:
    """テストデータ作成."""
    qids = []
    for t in [*[QuizType.TERM2SENT] * 2, QuizType.SENT2TERM]:
        qid = await create_quiz(
            sent_id,
            t,
            await _f(sent_id),
            user_uid=user_id,
        )
        qids.append(qid)
    return qids


@mark_async_test()
async def test_list_quiz_by_user_ids(u: LUser):
    """user_idからクイズを取得."""
    sent = LSentence.nodes.first(val="ccc")
    qid1, qid2, qid3 = await setup(sent.uid, u.uid)
    # 他のuserのクイズは取得されない
    u2 = await LUser(email="quiz2@ex.com").save()
    await create_quiz(
        sent.uid,
        QuizType.TERM2SENT,
        await _f(sent.uid),
        user_uid=u2.uid,
    )

    qs = await list_quiz_by_user_ids([u.uid])
    assert [q.quiz_id for q in qs.data.root] == [qid3, qid2, qid1]


@mark_async_test()
async def test_list_quiz_by_sentence_id(u: LUser):
    """user_idからクイズを取得."""
    sent = LSentence.nodes.first(val="ccc")
    qid1, qid2, qid3 = await setup(sent.uid, u.uid)
    qs = await list_quiz_by_sentence_ids([sent.uid])
    assert [q.quiz_id for q in qs.data.root] == [qid3, qid2, qid1]
    sent2 = LSentence.nodes.first(val="ccc1")
    qs = await list_quiz_by_sentence_ids([sent2.uid])
    assert len(qs.data.root) == 0


# resourceを指定してのクエリ
# 検索方式のenum指定
