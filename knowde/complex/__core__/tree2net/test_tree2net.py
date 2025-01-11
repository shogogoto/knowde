"""test."""


import pytest

from knowde.complex.__core__.tree2net import parse2net
from knowde.primitive.__core__.nxutil import EdgeType, to_nested
from knowde.primitive.heading import get_heading_path, get_headings
from knowde.primitive.term.errors import MarkUncontainedError


def test_add_block() -> None:
    """blockを正しく配置."""
    _s = """
        # h1
            1
            2
                21
            3
                31
                32
            4
                41
                42
                    421
                43
                    431
                    432
                44
                    441
                    442
                        4421
                        4422
                        4423
    """
    sn = parse2net(_s)
    assert list(EdgeType.BELOW.succ(sn.g, sn.root)) == ["1"]
    assert to_nested(sn.g, "1", EdgeType.SIBLING.succ) == {"2": {"3": {"4": {}}}}
    assert list(EdgeType.BELOW.succ(sn.g, "2")) == ["21"]
    assert to_nested(sn.g, "21", EdgeType.SIBLING.succ) == {}
    assert list(EdgeType.BELOW.succ(sn.g, "3")) == ["31"]
    assert to_nested(sn.g, "31", EdgeType.SIBLING.succ) == {"32": {}}
    assert list(EdgeType.BELOW.succ(sn.g, "4")) == ["41"]
    assert to_nested(sn.g, "41", EdgeType.SIBLING.succ) == {"42": {"43": {"44": {}}}}
    assert list(EdgeType.BELOW.succ(sn.g, "42")) == ["421"]
    assert to_nested(sn.g, "421", EdgeType.SIBLING.succ) == {}
    assert list(EdgeType.BELOW.succ(sn.g, "43")) == ["431"]
    assert list(EdgeType.BELOW.succ(sn.g, "44")) == ["441"]
    assert to_nested(sn.g, "441", EdgeType.SIBLING.succ) == {"442": {}}
    assert list(EdgeType.BELOW.succ(sn.g, "442")) == ["4421"]
    assert to_nested(sn.g, "4421", EdgeType.SIBLING.succ) == {"4422": {"4423": {}}}


def test_add_heading() -> None:
    """headingを正しく取得できる."""
    _s = """
        !c00
        # h1
        !c0
            aaa
        !c1
            bbb
                ccc
                eee
                !c2
                    eEE
        !c2
                    eeE
        ## h2
        !c3
            fff
            ggg
                -> ddd
        ### h3
            hhh
                iii
                <- jjj
    """
    sn = parse2net(_s)
    assert get_headings(sn.g, sn.root) == {"# h1", "## h2", "### h3"}
    assert get_heading_path(sn.g, sn.root, "ccc") == ["# h1"]
    assert get_heading_path(sn.g, sn.root, "eEE") == ["# h1"]
    assert get_heading_path(sn.g, sn.root, "eeE") == ["# h1"]
    assert get_heading_path(sn.g, sn.root, "ddd") == ["# h1", "## h2"]
    assert get_heading_path(sn.g, sn.root, "iii") == ["# h1", "## h2", "### h3"]
    assert get_heading_path(sn.g, sn.root, "jjj") == ["# h1", "## h2", "### h3"]


def test_add_ctx() -> None:
    """文脈."""
    _s = """
        # h1
            aaa
                <-> anti aaa\
                        aaa
            B: bbb
            C{B}: ccc
                -> D: d{CB}d
                    vvv
                    www
    """

    sn = parse2net(_s)
    assert list(EdgeType.SIBLING.succ(sn.g, "bbb")) == ["ccc"]
    assert list(EdgeType.TO.succ(sn.g, "ccc")) == ["d{CB}d"]
    assert list(EdgeType.SIBLING.succ(sn.g, "ccc")) == []
    assert list(EdgeType.TO.pred(sn.g, "d{CB}d")) == ["ccc"]
    assert to_nested(sn.g, "d{CB}d", EdgeType.BELOW.succ) == {"vvv": {}}
    assert to_nested(sn.g, "vvv", EdgeType.SIBLING.succ) == {"www": {}}
    # 両方向
    assert list(EdgeType.ANTI.succ(sn.g, "aaa")) == ["anti aaaaaa"]
    assert list(EdgeType.ANTI.pred(sn.g, "anti aaaaaa")) == ["aaa"]


def test_replace_quoterm() -> None:
    """引用用語."""
    _s = """
        # h1
            A: aaa
                aAA
                aBB
            B: bbb
        ## h2
            `A`
                ccc
                ddd
    """

    sn = parse2net(_s)
    assert to_nested(sn.g, "aaa", EdgeType.SIBLING.succ) == {"bbb": {}}
    # belowを1つに統合しようと思ったけどやめた
    assert to_nested(sn.g, "aaa", EdgeType.BELOW.succ) == {
        "aAA": {},
        "ccc": {},
    }


def test_duplicate_def_sentence() -> None:
    """エラー再現(定義文重複、引用用語)."""
    _s = """
        # 科学哲学
          人間と自然を分離させたニュートン力学を批判
            by. フリードリヒ・ヴィルヘルム・シェリング, シェリング:
          ウィラード・ファン・オルマン・クワイン: 論理実証主義を支持しつつ反対
            還元主義の否定
              決定的実験: 競合する２つの理論を決着させる適切な実験
                ピエール・デュエム, デュエム:
        ## 18. フランスの伝統
          フランスは伝統故に論理実証主義と距離を保ってきた
            `デュエム`
              物理理論は１つの説明というより数学的命題の体系
    """
    parse2net(_s)


def test_non_dupedge() -> None:
    """なんかBELOW Edgeで重複起きた."""
    # 電磁気学の創始者-[BELOW]->マクスウェル
    _s = """
        # h1
        ## 2. 科学哲学の始まり
          ペテン: 奥義が隠されているという見せかけ
          「科学哲学」という語彙の初出: 形而上学という{ペテン}から人間精神を開放しよう
            諸科学のクラス分けの着想
              by. アンドレ=マリー・アンペール, アンペール: 電磁気学の創始者
                when. 1775 ~ 1836
                where. フランス
                電気におけるニュートンと称された
                  by. マクスウェル:
                    when. 1831 ~ 79
                    where. イギリス
                カントを愛読していた
              by. オーギュスト・コント, コント:
                when. 1789 ~ 1857
                「基礎科学の哲学はベーコンの探求した第一哲学を構成するのに充分なのだ」

            # イギリス哲学の語彙に加える
            #   when. 1804
              by. ウィリアム。ヒューウェル: ケンブリッジ大学道徳哲学の教授
                when. 1794 ~ 18, succ6
                yield succ
          # ペテン:
    # """


def test_alias_resolve_error() -> None:
    """エラー再現(alias引用でMarkUncontainedError)."""
    _s = """
    # x
        AU |{アリストテレス}の宇宙: 月より内側が変化する世界、外側は不可侵の永久不変領域
          <-> ケプラーの超新星: 急に現れて天文学者たちを驚かせた
            when. 1604/10/9 ~
            ガリレオは視差が月より小さいことより{ケプラーの超新星}が月の外側にあると証明
              {AU}が誤りであることを決定づけた
          <-> ティコの超新星: {AU}の最初の反証
            when. 1572
            by. ティコ・ブラーエ, ティコ: デンマークの天文学者
              when. 1546 ~ 1601
    """
    with pytest.raises(MarkUncontainedError):
        _sn = parse2net(_s)  # アリストテレス が未定義


def test_regression() -> None:
    """再現."""
    _s = """
    # x
      選択公理: 空でない集合各々...
        空でない自然数の集合でも各集合の最小の要素を選べば自明に真
        無限集合で選び方が定義出来ない場合に自明ではない
          -> 他の公理から{選択公理}を証明できないか議論が巻き怒った
      構成主義: 実在するものは全て明示的に構成可能でなければならない
        {選択公理}を非難
      連続体仮説: 自然数の濃度と実数の濃度の中間は存在しない
      複数の妥当な集合論が成立
        <- {選択公理}と{連続体仮説}は独立に成り立つ
          by. ポール・コーエン: アメリカの数学者
            when. 1934 ~ 2007
      神の公理, 選択公理: 神でもなければ到底実行できない操作をできるとする

    """
    _sn = parse2net(_s)
