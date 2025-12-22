"""誤答肢の生成."""

from knowde.conftest import async_fixture
from knowde.shared.user.label import LUser


@async_fixture()
async def u() -> LUser:  # noqa: D103
    return await LUser(email="quiz@ex.com").save()


# クイズ作って質問を見て答えて成績を見る
# @pytest.mark.skip
# @mark_async_test()
# async def test_create_quiz(u: LUser):
#     """クイズを永続化."""
#     s = """
#         # title
#             aaa
#             bbb
#             parent
#                 c: ccc
#                     T1: ccc1
#                     T2: ccc2
#                     T3: ccc3
#                     -> to
#                         T4: todetail
#                         -> ccc5
#                     <- ccca
#                     <- cccb
#                         <- cccb1
#                     ex. ex1
#                         ex. ex2
#                     xe. ab1
#     """
#     _sn, _m = await save_text(u.uid, s)
#     sent = LSentence.nodes.first(val="ccc")
#     quiz_uid = await create_term2sent_quiz(sent.uid, radius=15, n_option=16)
#
#     qs = await restore_quiz([quiz_uid])
#     # # sleep(1000)
#     #
#     raise AssertionError
