"""usecase."""

from knowde.integration.quiz.domain.collections import ReadableQuizCollection
from knowde.integration.quiz.repo.create import generate_quiz
from knowde.integration.quiz.router.params import CreateQuizParam
from knowde.shared.types import UUIDy


async def create_quiz_uc(
    param: CreateQuizParam,
    user_uid: UUIDy,
) -> ReadableQuizCollection:
    """単文当てクイズ作成usecase."""
    src = await generate_quiz(
        param.quiz_type,
        param.cand_type,
        param.target_sent_uid,
        param.n_option,
        user_id=user_uid,
    )
    rq = src.to_readable()
    return ReadableQuizCollection(root=[rq])


# async def batch_create_quiz_uc(
#     param: BatchCreateQuizParam,
#     user_uid: UUIDy | None = None,
# ) -> ReadableQuizList:
#     """バッチ処理などで利用する単文当てクイズ作成usecase."""
#     tgt_uids = await list_candidates(
#         param.target_sent_uid,
#         param.cand_type,
#         must_has_term=True,
#     )
#
#     return await create_quiz_uc(param, user_uid)
