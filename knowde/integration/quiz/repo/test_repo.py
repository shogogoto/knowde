"""誤答肢の生成."""

from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.resource.usecase import save_text
from knowde.integration.quiz.repo.repo import create_term2sent_quiz
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser


@async_fixture()
async def u() -> LUser:  # noqa: D103
    user = await LUser(email="quiz@ex.com").save()
    s = """
        # title
            aaa
            bbb
            parent
                c: ccc
                    T1: ccc1
                    T2: ccc2
                    T3: ccc3
                    -> to
                        T4: todetail
                        -> ccc5
                    <- ccca
                    <- cccb
                        <- cccb1
                    ex. ex1
                        ex. ex2
                    xe. ab1
    """
    # T4: todetail -[親]-> parent -[前提]-> ccc が見つかってしまう
    # そんなクイズは非直感的で要らない気がする
    # でもそれは選択肢決定ロジックの責任ということで
    _sn, _m = await save_text(user.uid, s)
    return user


# クイズ作って質問を見て答えて成績を見る
@mark_async_test()
async def test_create_restore_term2sent(u: LUser):
    """クイズを永続化&復元."""
    sent = LSentence.nodes.first(val="ccc")
    n_option = 16
    quiz_uid = await create_term2sent_quiz(sent.uid, radius=99, n_option=n_option)
    srcs = await restore_quiz_sources([quiz_uid])
    assert len(srcs) == 1
    src = srcs[0]
    assert len(src.sources) == n_option - 1


# @mark_async_test()
# async def test_create_restore_sent2term(u: LUser):
#     """クイズを永続化&復元."""
#     sent = LSentence.nodes.first(val="ccc")
#     n_option = 16
#     quiz_uid = await create_term2sent_quiz(sent.uid, radius=99, n_option=n_option)
#     srcs = await restore_quiz_sources([quiz_uid])
#     assert len(srcs) == 1
#     src = srcs[0]
#     assert len(src.sources) == n_option - 1
