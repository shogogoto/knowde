"""test."""

from uuid import UUID

from fastapi.testclient import TestClient
from pytest_unordered import unordered

from knowde.api import root_router
from knowde.conftest import async_fixture, mark_async_test
from knowde.feature.knowde.repo import save_text
from knowde.feature.parsing.sysnet import SysNet
from knowde.shared.knowde.label import LSentence
from knowde.shared.nxutil import to_leaves, to_roots
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
    """parent(resourceに辿れる)の末尾 upper を取得する."""
    _sn = await setup(u)

    def s_assert(val: str, expected: str):
        s = LSentence.nodes.get(val=val)
        upper = knowde_upper(UUID(s.uid))
        assert upper.val == expected

    # そのまま辿れるなら自身を返す
    s_assert("0", "0")
    s_assert("p2", "p2")
    s_assert("x23", "x23")
    s_assert("x231", "x231")
    s_assert("yyy", "yyy")
    s_assert("zzz", "zzz")
    # upperがない場合は自身を返す
    s_assert("a", "a")
    s_assert("c{B}c", "c{B}c")
    # -> の upperも辿れる
    s_assert("1", "0")
    s_assert("2", "0")
    s_assert("11", "0")
    s_assert("22", "0")
    s_assert("221", "0")

    # <- の upperも辿れる
    s_assert("-1", "0")
    s_assert("-2", "0")
    s_assert("-11", "0")
    s_assert("-22", "0")
    # ->と<- の混在
    s_assert("complex1", "0")
    s_assert("complex2", "0")


@mark_async_test()
async def test_parents(u: LUser):
    """parentを取得(upstreamのbelow関係のみ、siblingは含まない."""


@mark_async_test()
async def test_detail_networks_to_or_resolved_edges(u: LUser):
    """IDによる詳細 TO/RESOLVED関係."""
    await setup(u)
    s = LSentence.nodes.get(val="0")
    detail_0 = chains_knowde(UUID(s.uid))
    assert [k.sentence for k in detail_0.succ("0", EdgeType.TO)] == unordered([
        "1",
        "2",
    ])
    roots_to = to_roots(detail_0.g, EdgeType.TO)
    assert [detail_0.knowdes[s].sentence for s in roots_to] == unordered([
        "-11",
        "-12",
        "-21",
        "-22",
        "complex2",
    ])
    leaves_to = to_leaves(detail_0.g, EdgeType.TO)
    assert [detail_0.knowdes[s].sentence for s in leaves_to] == unordered([
        "11",
        "12",
        "21",
        "221",
        "complex1",
    ])
    roots_ref = to_roots(detail_0.g, EdgeType.RESOLVED)
    leaves_ref = to_leaves(detail_0.g, EdgeType.RESOLVED)
    assert [detail_0.knowdes[s].sentence for s in roots_ref] == unordered([
        "c{B}c",
    ])

    assert [detail_0.knowdes[s].sentence for s in leaves_ref] == unordered([
        "0",
        "a",
    ])

    assert [p.sentence for p in detail_0.part("0")] == unordered([
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

    loc = detail_0.location
    assert loc.user.id == UUID(u.uid)
    assert [f.val for f in loc.folders] == ["A", "B"]
    assert loc.resource.name == "# titleX"
    assert [f.val for f in loc.headers] == ["## head1", "### head2"]
    assert [str(p) for p in loc.parents] == [
        "parentT(19C)",
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
    assert d.location.headers == []
    assert d.location.user.id.hex == u.uid
    assert d.location.parents == []


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
    """
    _sn, _r = await save_text(u.uid, s)
    tgt = LSentence.nodes.first(val="物理的実在の世界")
    client = TestClient(root_router())
    res = client.get(f"/knowde/sentence/{tgt.uid}")
    assert res.is_success
    uid = UUID(tgt.uid)
    res = client.get(f"/knowde/sentence/{uid}")
    assert res.is_success


@mark_async_test()
async def test_location_by_by_regression(u: LUser):
    """<- by. の連鎖ではlocationが not foundになっていたので修正."""
    s = """
    # title
      ZF公理系, ツェルメロ=フレンケルの公理系: 集合論を矛盾なく公理化・再現した
        by. エルンスト・ツェルメロ: ドイツの数学者
          when. 1871 ~ 1953
      選択公理: 空でない集合各々から要素を選び出して新しい集合を作れる
      連続体仮説: 自然数の濃度と実数の濃度の中間は存在しない
      複数の妥当な集合論が成立
        <- {選択公理}と{連続体仮説}は{ZF公理系}と矛盾しない
          by. クルト・ゲーテル, ゲーテル: 最も偉大な論理学者の一人
            when. 1906 ~ 1978
    """

    _sn, _r = await save_text(u.uid, s)
    client = TestClient(root_router())

    tgt = LSentence.nodes.first(val="ドイツの数学者")
    res = client.get(f"/knowde/sentence/{tgt.uid}")
    assert res.is_success

    tgt = LSentence.nodes.first(val="最も偉大な論理学者の一人")
    res = client.get(f"/knowde/sentence/{tgt.uid}")
    assert res.is_success
