"""knowde router test."""

from datetime import datetime
from uuid import UUID

import pytz
from fastapi import status
from fastapi.testclient import TestClient

from knowde.api import root_router
from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.entry.resource.usecase import save_text
from knowde.feature.knowde import KnowdeDetail
from knowde.shared.knowde.label import LSentence, LTerm
from knowde.shared.user.label import LUser


@async_fixture()
async def u() -> LUser:  # noqa: D103
    return await LUser(email="onex@gmail.com", hashed_password="xxx").save()  # noqa: S106


@mark_async_test()
async def test_detail_router(u: LUser, caplog):
    """Router testは1つはしておくけど細かいケースはrepositoryなどでやっておく."""
    client = TestClient(root_router())
    res = client.get("/knowde/sentence/064ef00c-5e33-4505-acf5-45ba26cc54dc")
    assert res.status_code == status.HTTP_404_NOT_FOUND

    s = """
    # titleX
    ## head1
    ### head2
        parent
            when. 19C
            p1
            p2
                p21
            p3
    """
    t = datetime.now(tz=pytz.timezone("Asia/Tokyo"))
    _sn, _r = await save_text(
        u.uid,
        s,
        # DB readしたときにneo4j.DateTimeが返ってきて
        # pydanticとvalidate error にならないかチェック
        updated=t,
        path=("A", "B", "C.txt"),
    )

    s = LSentence.nodes.get(val="p21")
    url = f"/knowde/sentence/{UUID(s.uid)}"
    res = client.get(url)

    assert res.status_code == status.HTTP_200_OK
    d = KnowdeDetail.model_validate(res.json())

    assert d.location.resource.updated == t
    assert d.location.user.id.hex == u.uid
    assert [f.val for f in d.location.folders] == ["A", "B"]


@mark_async_test()
async def test_search(u: LUser, caplog):
    """本番でのapi callを模擬(重いからskip."""
    s = """
    # 神は数学者か?
      @author マオリ・リヴィオ
      @published 2017

    ## 1. 謎

      数学の偏在性と全能性:

      「宇宙はまるで純粋数学者が設計したかのようだ」
        by. ジェームズ・ジーンズ
          イギリスの宇宙物理学者 1877-1946

      P1 |「数学は、経験とは無関係な思考の産物なのに、\
        なぜ物理的実在の対称物にこれほどうまく適合するのか」

      リヴァイアサンの記述
        真理とは、私達が断定を行う際に名称を正しく並べること
        幾何学は神が人類に与え給うた唯一の学問
          定義: 言葉の意味を定める
            計算の初めに置く

      ロジャー・ペンローズ=ペンローズ: オックスフォード大学の著名な数理物理学者

      ペンローズの３世界:
        1. 精神世界: 人間の表象の世界
        2. 物質世界: 物理的実在の世界
        3. 数学世界: プラトン主義の数学的形式の世界、イデア界
          ex. ユークリッド幾何学、ニュートンの運動法則、ひも理論などの数学的モデル

      アルキメデス:
        when. -287 ~ -212
        近代のニュートンやガウスレベルの人物
        父は天文学者ペイディアス、太陽と月の直径比を推定した
        若い頃にアレクサンドリアで数学を学んだ後に故郷シュラクサイに戻って研究に没頭
          食事や体の世話も疎かに研究
        抽象数学の美を名誉とし、それ以外の機械など技術一般は実用目的の卑賤なもの
    """
    client = TestClient(root_router())
    _sn, _r = await save_text(u.uid, s)
    s = LTerm.nodes.get(val="アルキメデス").sentence.single()
    url = "/knowde/?q=%E6%95%B0%E5%AD%A6&type=CONTAINS&page=1&size=100&n_detail=1&n_premise=3&n_conclusion=3&n_refer=3&n_referred=3&dist_axiom=1&dist_leaf=1&desc=true"  # noqa: E501
    res = client.get(url)
    assert res.status_code == status.HTTP_200_OK
