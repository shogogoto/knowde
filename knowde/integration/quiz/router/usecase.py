"""usecase."""

from knowde.integration.quiz.distractor.distractor import fetch_distractor_ids
from knowde.integration.quiz.domain.build import build_readable
from knowde.integration.quiz.domain.domain import ReadableQuizList
from knowde.integration.quiz.repo.create import create_quiz_and_correct
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.integration.quiz.router.params import CreateQuizParam
from knowde.shared.types import UUIDy


async def create_quiz_uc(
    param: CreateQuizParam,
    user_uid: UUIDy | None = None,
) -> ReadableQuizList:
    """単文当てクイズ作成usecase."""
    uids = await fetch_distractor_ids(
        [param.target_sent_uid],
        param.cand_type,
        limit=param.n_option - 1,
        must_has_term=param.quiz_type.has_term,
    )
    quiz_uid = await create_quiz_and_correct(
        param.target_sent_uid,
        param.quiz_type,
        uids,
        user_uid=user_uid,
    )
    srcs = await restore_quiz_sources([quiz_uid])
    return ReadableQuizList(root=[build_readable(s) for s in srcs])


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
