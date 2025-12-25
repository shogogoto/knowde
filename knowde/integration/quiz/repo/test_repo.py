"""誤答肢の生成."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.domain.parts import QuizRel, QuizType
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.repo.repo import (
    create_quiz,
)
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.integration.quiz.repo.select_option.selector import select_random_options
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser

u = async_fixture()(fx_u)


# クイズ作って質問を見て答えて成績を見る
@mark_async_test()
async def test_create_restore_term2sent(u: LUser):
    """クイズを永続化&復元."""
    sent = LSentence.nodes.first(val="ccc")
    n_option = 16
    quiz_uid = await create_quiz(
        sent.uid,
        QuizType.TERM2SENT,
        option_uids=await select_random_options(
            sent.uid,
            radius=99,
            n_option=n_option,
        ),
    )
    srcs = await restore_quiz_sources([quiz_uid])
    assert len(srcs) == 1
    src = srcs[0]
    assert len(src.sources) == n_option - 1
    # 関係が取れているのを１つ確認
    assert src.get_by_sent("ccc3").rels == [QuizRel.DETAIL]


# @mark_async_test()
# async def test_create_restore_sent2term(u: LUser):
#     """クイズを永続化&復元."""
#     sent = LSentence.nodes.first(val="ccc")
#     n_option = 16
#     quiz_uid = await create_quiz(
#         sent.uid,
#         QuizType.SENT2TERM,
#         radius=99,
#         n_option=n_option,
#     )
#     srcs = await restore_quiz_sources([quiz_uid])
#     assert len(srcs) == 1
#     src = srcs[0]
#     assert len(src.sources) == n_option - 1
