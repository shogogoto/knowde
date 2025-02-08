"""test."""


import pytest

from knowde.complex.__core__.tree2net import parse2net
from knowde.primitive.term.errors import MarkUncontainedError


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
