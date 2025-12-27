"""quiz router test."""

from httpx import AsyncClient

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.domain.domain import ReadableQuiz
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.router.params import CreateQuizParam
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser
from knowde.shared.user.testing import aauth_header

u = async_fixture()(fx_u)


@mark_async_test()
async def test_sent2term(ac: AsyncClient, u: LUser):
    """単文から用語を当てるクイズの一連の流れ."""
    sent = LSentence.nodes.first(val="ccc")
    p = CreateQuizParam(
        target_sent_uid=sent.uid,
        quiz_type=QuizType.SENT2TERM,
        radius=4,
        n_option=4,
    )

    h = await aauth_header(email=u.email)
    # クイズ作成
    res = await ac.post(
        "/quiz",
        json=p.model_dump(),
        headers=h,
    )
    rq = ReadableQuiz.model_validate(res.json())
    # print(rq.string)
    # print(rq.model_dump_json(indent=2))

    # クイズに回答
    res = await ac.post(
        f"/quiz/answer/{rq.quiz_id}",
        json={"selected": rq.correct},
        headers=h,
    )

    # sleep(1000)
    # 正解がどれかや他の選択肢の解説など
    #   クイズチェーンに繋がるような情報も返す
    #   過去の回答も返す(正答率)
    #
    # raise AssertionError
