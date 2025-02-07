"""時系列.

# CLIで何を表示するか

# 期間
暗黙の期間 ex. 1000 -> 1000/01/01 ~ 1000/12/31 みたいな
# 月の期間を定義
    1000/1/1 ~  終わりが不定
    ~ 1111/11/11  始まりが不定
    1000/1/1 ~ 1111/11/11 決まってる


# **時系列でソート**


    重なった期間をどう表現するか
    intervaltree
        区間の重なり検索が高速
        メモリ効率が良い
        特に期間の重なりチェックに特化
"""
import pytest
from pytest_unordered import unordered

from knowde.primitive.__core__.types import Duplicable
from knowde.primitive.time.errors import EndBeforeStartError

from . import Series, parse_when


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("1000 ~", "1000/.."),
        ("~ 1200", "../1200"),
        ("1000 ~ 1200", "1000/1200"),
        ("1200~", "1200~"),
        ("1200 ~ 1300/12/1", "1200/1300-12-01"),
    ],
)
def test_interval(string: str, expected: str) -> None:
    """EDTFではなく独自のInterval."""
    when = parse_when(string)
    ex = parse_when(expected)
    assert when.lower_strict() == ex.lower_strict()
    assert when.upper_strict() == ex.upper_strict()


def test_invalid_interval() -> None:
    """不正な期間."""
    with pytest.raises(EndBeforeStartError):
        Series.create(["1831 ~ 79"])


def test_series() -> None:
    """時系列のソート."""
    dup1 = Duplicable(n="2004")
    dup2 = Duplicable(n="2004")
    ser = Series.create(
        [
            "2000/1 ~ 2025",
            "2004/12",
            "2004",
            "2004/12",
            dup1,
            dup2,
            "2001",
            "1950/7/7",
            "1945",
            "-02XX",
        ],
    )
    assert ser.overlap("2002 ~ 2005") == unordered(
        [
            "2000/1 ~ 2025",
            dup1,
            dup2,
            "2004",
            "2004/12",
        ],
    )
    assert ser.overlap("2004/11") == unordered(["2000/1 ~ 2025", dup1, dup2, "2004"])
    assert ser.overlap("2002") == ["2000/1 ~ 2025"]
    assert ser.overlap("1945/1/2") == ["1945"]
    assert ser.envelop("~ 1949") == ["-02XX", "1945"]
