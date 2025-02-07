"""test."""


import pytest

from knowde.complex.__core__.tree2net import parse2net
from knowde.primitive.parser.errors import AttachDetailError
from knowde.primitive.term.errors import MarkUncontainedError


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
          アンドレ=マリー・アンペール, アンペール: 電磁気学の創始者
            when. 1775 ~ 1836
            電気におけるニュートンと称された
              by. マクスウェル: xxx
                when. 1831 ~ 79
                  aa
    """
    with pytest.raises(AttachDetailError):
        parse2net(_s)


def test_alias_resolve_error() -> None:
    """エラー再現(alias引用でMarkUncontainedError)."""
    _s = """
    # x
        AU |{アリストテレス}の宇宙: 月より内側が変化する世界、外側は不可侵の永久不変領域
          <-> ケプラーの超新星: 急に現れて天文学者たちを驚かせた
            when. 1604/10/9 ~
            ガリレオは視差が月より小さいことより{ケプラーの超新星}が月の外側にあると証明
              {AU}が誤りであることを決定づけた
    """
    with pytest.raises(MarkUncontainedError):
        _sn = parse2net(_s)  # アリストテレス が未定義


@pytest.mark.skip()
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
