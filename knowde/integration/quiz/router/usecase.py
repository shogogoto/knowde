"""usecase."""

from knowde.integration.quiz.candidate.candidate import (
    list_candidates,
)
from knowde.integration.quiz.domain.build import build_readable
from knowde.integration.quiz.domain.domain import ReadableQuizList
from knowde.integration.quiz.repo.create import create_quiz
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.integration.quiz.router.params import CreateQuizParam
from knowde.integration.quiz.sampling.sample_safe import (
    sample_safe,
)
from knowde.shared.types import UUIDy


async def create_quiz_uc(
    param: CreateQuizParam,
    user_uid: UUIDy | None = None,
) -> ReadableQuizList:
    """単文当てクイズ作成usecase."""
    cand_uids = await list_candidates(
        param.target_sent_uid,
        param.cand_type,
        must_has_term=True,
    )
    sample_uids = sample_safe(cand_uids, n_option=param.n_option)

    quiz_uid = await create_quiz(
        param.target_sent_uid,
        param.quiz_type,
        sample_uids,
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
