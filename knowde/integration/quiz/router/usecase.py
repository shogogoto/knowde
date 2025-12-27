"""usecase."""

from knowde.integration.quiz.domain.build import build_readable
from knowde.integration.quiz.domain.domain import ReadableQuiz
from knowde.integration.quiz.repo.repo import create_quiz
from knowde.integration.quiz.repo.restore import restore_quiz_sources
from knowde.integration.quiz.repo.select_option.candidate import (
    list_candidates_by_radius,
)
from knowde.integration.quiz.repo.select_option.sample import sample_options_randomly
from knowde.integration.quiz.router.params import CreateQuizParam
from knowde.shared.types import UUIDy


async def create_term2sent_quiz_usecase(
    param: CreateQuizParam,
    user_uid: UUIDy | None = None,
) -> ReadableQuiz:
    """単文当てクイズ作成UC."""
    # 候補選択ロジックをparamで指定するのは難しい
    # ハードコードしてしまっていて微妙
    # 候補選択ロジックの引数の共通化ができれば、Enumで切り替えを実現できそう
    #   n_option, has_termは共通
    #   半径はランダムとスコアで非共通な引数
    #      retryによる半径調整やスコア
    #
    cand_uids = await list_candidates_by_radius(
        param.target_sent_uid,
        radius=param.radius,
        has_term=True,
    )
    sample_uids = sample_options_randomly(cand_uids, n_option=param.n_option)

    quiz_uid = await create_quiz(
        param.target_sent_uid,
        param.quiz_type,
        sample_uids,
        user_uid=user_uid,
    )
    srcs = await restore_quiz_sources([quiz_uid])
    return build_readable(srcs[0])
