"""quiz router test."""

from httpx import AsyncClient

from knowde.conftest import async_fixture, mark_async_test
from knowde.integration.quiz.domain.domain import Answer, ReadableQuiz
from knowde.integration.quiz.domain.parts import QuizType
from knowde.integration.quiz.fixture import fx_u
from knowde.integration.quiz.router.params import CreateQuizParam
from knowde.shared.knowde.label import LSentence
from knowde.shared.user.label import LUser
from knowde.shared.user.testing import aauth_header

u = async_fixture()(fx_u)


@mark_async_test()
async def test_sent2term(ac: AsyncClient, u: LUser):
    """単文から用語を当てるクイズの一連の流れ.

    単文idとクイズタイプを決める
    選択肢候補の出し方を指定する
        選択肢候補の数を指定する
        既定の候補出しのロジックをEnumで指定する方針にするか
    quizを永続化
    回答できるような可読問題を返す


    それを受け付けて回答を永続化
    その回答と関連する情報をフィードバック
        回答の正否
        同じクイズ対象の他の問題一覧
        関連クイズ
        同一クイズの過去の回答履歴、正答率

    クイズチェーンとは
        閲覧に能動的なユーザー操作の循環を与えるもの
            単文一覧を眺めたり、その関係を追ったりできるだけでは復習する動機に欠ける


    """
    sent = LSentence.nodes.first(val="ccc")
    p = CreateQuizParam(
        target_sent_uid=sent.uid,
        quiz_type=QuizType.SENT2TERM,
        radius=4,  # ここを決め打ち選択肢ロジックのEnum指定に置き換える
        n_option=4,
    )

    h = await aauth_header(email=u.email)
    res = await ac.post(
        "/quiz",
        json=p.model_dump(),
        headers=h,
    )
    rq = ReadableQuiz.model_validate(res.json())
    res = await ac.post(
        f"/quiz/answer/{rq.quiz_id}",
        json={"selected": rq.correct},
        headers=h,
    )
    ans = Answer.model_validate(res.json())
    assert ans.is_correct
    # 不正解
    res = await ac.post(
        f"/quiz/answer/{rq.quiz_id}",
        json={"selected": rq.distractors},
        headers=h,
    )
    ans = Answer.model_validate(res.json())
    assert not ans.is_correct
    assert ans.who.username == "quiz"
