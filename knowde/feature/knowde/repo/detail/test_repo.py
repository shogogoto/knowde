"""test."""

from uuid import UUID

from fastapi.testclient import TestClient
from pytest_unordered import unordered

from knowde.api import root_router
from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.knowde.repo import save_text
from knowde.feature.parsing.sysnet import SysNet
from knowde.feature.stats.nxdb import LSentence
from knowde.shared.nxutil import nxprint, to_leaves, to_roots
from knowde.shared.nxutil.edge_type import EdgeType
from knowde.shared.user.label import LUser

from . import chains_knowde, knowde_upper


@async_fixture()
async def u() -> LUser:  # noqa: D103
    return await LUser(email="one@gmail.com", username="one").save()


async def setup(u: LUser) -> SysNet:  # noqa: D103
    s = """
    # titleX
    ## head1
    ### head2
        parent
            when. 19C
            p1
            p2
                zero, re :0
                    when. R10/11/11
                    xxx
                        x1
                            x11
                            x12
                        x2
                            x21
                            x22
                            x23
                                x231
                    yyy
                    zzz
                    <- -1
                        when. 1919
                        <- -11
                        <- -12
                    <- -2
                        <- -21
                        <- -22
                            -> complex1
                                <- complex2
                    -> 1
                        -> 11
                        -> 12
                    -> 2
                        -> 21
                        -> 22
                            -> 221
        A: a
        B: b{A}b{zero}
        C: c{B}c
            -> ccc
    """
    sn, _r = await save_text(
        u.uid,
        s,
        path=("A", "B", "C.txt"),
    )  # C.txtはDBには格納されない
    return sn


@mark_async_test()
async def test_get_upper(u: LUser):
    """parentの末尾 upper を取得する."""
    sn = await setup(u)
    nxprint(sn.g, detail=True)

    def s_assert(val: str, expected: str):
        s = LSentence.nodes.get(val=val)
        upper = knowde_upper(UUID(s.uid))
        assert upper.val == expected

    s_assert("0", "p2")
    s_assert("p2", "p1")
    s_assert("x23", "x22")
    s_assert("x231", "x23")
    s_assert("yyy", "xxx")
    s_assert("zzz", "yyy")
    # upperがない場合は自身を返す
    s_assert("a", "parent")
    s_assert("c{B}c", "b{A}b{zero}")
    # -> の upperも辿れる
    s_assert("1", "p2")
    s_assert("2", "p2")
    s_assert("11", "p2")
    s_assert("22", "p2")
    s_assert("221", "p2")

    # <- の upperも辿れる
    s_assert("-1", "p2")
    s_assert("-2", "p2")
    s_assert("-11", "p2")
    s_assert("-22", "p2")
    # ->と<- の混在
    s_assert("complex1", "p2")
    s_assert("complex2", "p2")


@mark_async_test()
async def test_detail_networks_to_or_resolved_edges(u: LUser):
    """IDによる詳細 TO/RESOLVED関係."""
    await setup(u)
    s = LSentence.nodes.get(val="0")
    detail = chains_knowde(UUID(s.uid))
    assert [k.sentence for k in detail.succ("0", EdgeType.TO)] == unordered([
        "1",
        "2",
    ])
    roots_to = to_roots(detail.g, EdgeType.TO)
    assert [detail.knowdes[UUID(s)].sentence for s in roots_to] == unordered([
        "-11",
        "-12",
        "-21",
        "-22",
        "complex2",
    ])
    leaves_to = to_leaves(detail.g, EdgeType.TO)
    assert [detail.knowdes[UUID(s)].sentence for s in leaves_to] == unordered([
        "11",
        "12",
        "21",
        "221",
        "complex1",
    ])
    roots_ref = to_roots(detail.g, EdgeType.RESOLVED)
    leaves_ref = to_leaves(detail.g, EdgeType.RESOLVED)
    assert [detail.knowdes[UUID(s)].sentence for s in roots_ref] == unordered([
        "c{B}c",
    ])

    assert [detail.knowdes[UUID(s)].sentence for s in leaves_ref] == unordered([
        "0",
        "a",
    ])

    assert [p.sentence for p in detail.part("0")] == unordered([
        "0",
        "xxx",
        "x1",
        "x11",
        "x12",
        "x2",
        "x21",
        "x22",
        "x23",
        "x231",
        "yyy",
        "zzz",
    ])

    loc = detail.location
    assert loc.user.id == UUID(u.uid)
    assert [f.val for f in loc.folders] == ["A", "B"]
    assert loc.resource.name == "# titleX"
    assert [f.val for f in loc.headers] == ["## head1", "### head2"]
    assert [str(p) for p in loc.parents] == [
        "parentT(19C)",
        "p1",
        "p2",
    ]


@mark_async_test()
async def test_detail_no_below_no_header(u: LUser):
    """belowなしでも取得できるか."""
    s = """
    # titleX
        a
    """
    _sn, _r = await save_text(u.uid, s)
    s = LSentence.nodes.get(val="a")
    d = chains_knowde(UUID(s.uid))
    assert [k.sentence for k in d.part("a")] == ["a"]
    assert d.location.parents == []
    assert d.location.headers == []
    assert d.location.user.id.hex == u.uid


@mark_async_test()
async def test_detail_no_below_no_header_with_parent(u: LUser):
    """belowなしでも取得できるか."""
    s = """
    # titleX
        parent
            a
    """
    _sn, _r = await save_text(u.uid, s)
    s = LSentence.nodes.get(val="a")
    d = chains_knowde(UUID(s.uid))
    assert [k.sentence for k in d.part("a")] == ["a"]
    assert [k.sentence for k in d.location.parents] == ["parent"]
    assert d.location.headers == []
    assert d.location.user.id.hex == u.uid


@mark_async_test()
async def test_detail_no_header(u: LUser):
    """headerなし."""
    s = """
    # titleX
        a
            b
            c
        d
        e
            f
    """
    _sn, _r = await save_text(u.uid, s)
    s = LSentence.nodes.get(val="a")
    d = chains_knowde(UUID(s.uid))
    assert [k.sentence for k in d.part("a")] == unordered(["a", "b", "c"])
    assert d.location.parents == []
    assert d.location.headers == []
    assert d.location.user.id.hex == u.uid


@mark_async_test()
async def test_not_found_should_not_raise_error(u: LUser):
    """Regression test."""
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

      ロジャー・ペンローズ=ペンローズ: オックスフォード大学の著名な数理物理学者

      ペンローズの３世界:
        1. 精神世界: 人間の表象の世界
        2. 物質世界: 物理的実在の世界
        3. 数学世界: プラトン主義の数学的形式の世界、イデア界
          ex. ユークリッド幾何学、ニュートンの運動法則、ひも理論などの数学的モデル

      ペンローズの３つの謎:
        1. {物質世界}が{数学世界}の法則に従う
          ex. `P1`
          ! EF = EFfective
          ex. EF |数学の不条理な有効性:
            物理学の法則を定式化するのに数学という言語が似つかわしいというこの奇跡
            {物質世界}が{数学世界}に従うという謎
            by. ユージン・ウィグナー, ウィグナー: ノーベル賞を受賞した物理学者
              when. 1902 ~ 1995
        2. 心が{物質世界}から生まれる
        3. {ペンローズの３世界}が不思議なほど結びついている

      積極的な側面: 数学を応用して自然法則を構築するケース
        {EF}を信じて{物質世界}から数学的法則を導き出すこと
        ex. マクスウェル方程式、一般相対性理論
        <-> 受動的な側面: 数学が意図せずに{物質世界}に応用されること
          ハーディ: 純粋数学が{物質世界}に応用されるとは信じていなかった
            イギリスの変わり者の数学者
            when. 1877 ~ 1947
            「数論を戦争に役立たせる道は誰も見出していない」
              <-> 暗号に応用され
          ! nameの区切り文字を","に変えるべきか
          ハーディ=ワインベルクの法則: 進化の基本原理を説明する数学的モデル
            以下を満たす大規模の遺伝子恒星は世代間で変化しない
              無作為に交配する
              個体の流出なし
              突然変異なし
              自然選択が発生しない
          楕円の研究
            by. メナイクモス
              when. BC50
            太陽系の惑星の軌道の記述へ応用された
              by. ケプラー
              by. ニュートン
    """
    _sn, _r = await save_text(u.uid, s)
    tgt = LSentence.nodes.first(val="物理的実在の世界")
    client = TestClient(root_router())
    res = client.get(f"/knowde/sentence/{tgt.uid}")
    assert res.is_success
    uid = UUID(tgt.uid)
    res = client.get(f"/knowde/sentence/{uid}")
    assert res.is_success
